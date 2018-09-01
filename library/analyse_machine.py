#!/usr/bin/env python
# -*-coding:utf-8-*-


import logging
import itertools

from ansible.module_utils.basic import AnsibleModule
import yaml  # you have installed the ansible right?
from suitable import Api

DOCUMENTATION = '''
---
module: analyse_machine
short_description: 分析机器规划信息
description:
   - 分析 machine_variables.yml 文件引入的参量
   - 分析 machine_group 定义，根据输入的hosts参数智能的分配对应的ip。

options: {}
author:
    - "wanze"
'''

EXAMPLES = '''
1. ansible localhost -m "analyse_machine" -a "hosts=... " -vvv

'''


MACHINE_VARIABLES = "machine_variables.yml"
LOGFILE = './library_data/log/analyse_machine.log'

logging.basicConfig(filename=LOGFILE, level=logging.DEBUG)

"""
# item item item item item item item  ...
# 输入是可用机器信息 具体是 machine_info 
[{},{'facts':...}]

# model
# 具体这里的模型指的就是 machine_define 
[{},{},{'vars:...'}]

# 实例化后的模型产物

"""


def checking_ceph_osd(item, checking_item):
    """
    item 是模型定义
    checking_item 是输入的item
    """
    # 首先看模型定义是否需要ceph_osd True
    if not item['vars'].get('ceph_osd'):
        return True

    interfaces = checking_item['facts'].get('ansible_interfaces')
    try:
        interfaces.remove('lo')
    except ValueError:
        pass

    devices = checking_item['facts'].get('ansible_devices')
    if len(interfaces) > 1 and len(devices) > 1:  # 网卡要求 和硬盘要求
        return True
    else:
        return False


checking_condition_mapping = {
    'ceph_osd': checking_ceph_osd,
}


def modelling_sort(input_data, model, checking_condition_mapping):
    # 虽然比较低效但简单，暴力排列枚举
    input_list = list(itertools.permutations(input_data))

    def _modelling_sort(input_list, model, checking_condition_mapping):

        count = 0
        result = []

        for item in model:
            checking_item = input_list[0][count]

            for key in item.keys():
                if not checking_condition_mapping.get(key):  # 不需要检查
                    continue
                elif checking_condition_mapping[key](item, checking_item):
                    continue
                else:  # 匹配失败
                    # 重新安排input 再计算
                    input_list.pop(0)
                    _modelling_sort(input_list, model,
                                    checking_condition_mapping)
            else:
                item['host'] = checking_item['host']  # 其他facts都不需要
                result.append(item)
                count += 1
        else:
            return result

    while input_list:
        return _modelling_sort(input_list, model, checking_condition_mapping)
    else:
        raise Exception('can not find a solution')




def parse_machine_variables():
    """
    从 machine_variables.yml 中获取data
    """
    with open(MACHINE_VARIABLES, 'r') as stream:
        try:
            data = yaml.load(stream)
            return data
        except yaml.YAMLError as e:
            logging.error(e)


class AnalyseMachine(object):

    def __init__(self, module):
        self.module = module

        self.action = module.params['action']

        self.hosts = module.params['hosts']

        self.data = parse_machine_variables()

    def execute_command(self, cmd):
        return self.module.run_command(cmd)

    def analyse(self):
        machine_group = self.data['machine_group']

        machine_define = []
        index = 1
        for item in machine_group:
            if not item.get('group_machine_num'):
                continue
            else:
                for i in range(item['group_machine_num']):
                    host_info = {}
                    host_info['index'] = index  # 机器索引，方便后面给机器命名

                    host_info['hostname'] = self.calc_hostname(index)
                    host_info['group_name'] = item['group_name']
                    host_info['vars'] = item['group_vars']
                    machine_define.append(host_info)

                    index += 1

        logging.info('init machine_define: {0}'.format(machine_define))

        machine_info = self.setup()

        machine_define = modelling_sort(
            machine_info, machine_define, checking_condition_mapping)

        logging.info('last machine_define: {0}'.format(machine_define))
        return machine_define

    def calc_hostname(self, index):
        hostname_prefix = self.data['hostname_prefix']
        suffix = "%03d" % index
        hostname = "{0}{1}".format(hostname_prefix, suffix)
        return hostname

    def ping(self):
        ssh_username = self.data['ssh_username']
        ssh_password = self.data['ssh_password']
        hosts = Api(self.hosts, remote_user=ssh_username,
                    remote_pass=ssh_password, ignore_unreachable=True)

        data = hosts.ping()
        exist_host = data['contacted'].keys()  # 更新实际可连的hosts

        self.hosts = exist_host  # 自己的也更新下

        logging.info('update exist host to: {0}'.format(exist_host))
        return exist_host

    def setup(self):
        ssh_username = self.data['ssh_username']
        ssh_password = self.data['ssh_password']

        hosts = Api(self.hosts, remote_user=ssh_username,
                    remote_pass=ssh_password)

        machine_info = hosts.setup()

        result = []
        for host in self.hosts:
            item = {}
            item['host'] = host
            item['facts'] = machine_info['contacted'][host]['ansible_facts']
            result.append(item)

        machine_info = result
        logging.info('machine info is: {0}'.format(machine_info))
        return machine_info


def main():
    module = AnsibleModule(
        argument_spec=dict(
            action=dict(required=True, type='str'),
            hosts=dict(required=True, type='list'),
        ),
        supports_check_mode=True
    )

    analyse_machine = AnalyseMachine(module)

    rc = None
    out = ''
    err = ''
    result = {}
    result['ansible_facts'] = {}

    if analyse_machine.action == "ping":
        result['ansible_facts'] = {
            'exist_host': analyse_machine.ping()
        }
    elif analyse_machine.action == "analyse":
        machine_define = analyse_machine.analyse()

        # 稍微处理下方便后面取值
        machine_group = {}
        for index, item in enumerate(machine_define):
            machine_group[item['host']] = item

        result['ansible_facts']['machine_group'] = machine_group
    else:
        logging.error("unknown action name: {0}".format(
            analyse_machine.action))

        analyse_machine.module.fail_json(
            msg="unknown action name: {0}".format(analyse_machine.action))

    if rc is None:
        result['changed'] = False
    else:
        result['changed'] = True
    if out:
        result['stdout'] = out
    if err:
        result['stderr'] = err

    module.exit_json(**result)


# import module snippets
from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
