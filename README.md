# ansible_examples

## intro
every rule focus on some common task, Although there are docker or some other solution, but in some time , install software in linux system just make sense and have some convience. here are some ansible code , just remeber the linux operation.

写了很多碎片小任务，既可以作为脚本来刷，也可以参考学习。

## 安装基本步骤
1. 安装ansible，你可以执行 `install_ansible.sh` 这个脚本。

2. 运行脚本：
```
ansible-playbook -i hosts site.yml
```

3. 单独运行某个任务
```
ansible-playbook -i hosts site.yml --tags=task_name
```


## 子任务清单

### debug 
some debug info

只是一个打印debug信息的任务 并不会对系统进行任何修改 可以先运行下确认ansible工作正常

### prepare 
yum update  install epel and install Development tools

升级和安装centos Development tools 推荐

### prepare_user
install user and group

新建某个用户和群组

你可以在group_vars 的all 文件里面定义 user group user_home 


重复刷是没问题的

### python3
install python36 on centos

在centos上安装 python36 并新建 /usr/bin/python3 符号链接方便你直接输入 python3 调用


### postgresql
安装postgresql数据库 

你设置的 user 参数 将会当做用户名创建一个postgresql的新用户

### nginx
安装nginx 并复制网站配置过去




### airflow
安装apache-airflow，主要是配置好airflow webserver和 airflow scheduler 这两个服务。 可做参考


### elasticsearch
安装elasticsearch

### mongodb
show how to install mongodb


### apache
apache从零开始编译到django相关配置等，可做参考，默认不开启。


