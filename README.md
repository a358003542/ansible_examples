# ansible_examples

## intro
every rule focus on some common task, Although there are docker or some other solution, but in some time , install software in linux system just make sense and have some convience. here are some ansible code , just remeber the linux operation.



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

### prepare 
yum update  install epel and install Development tools


### prepare_user
install user and group

### python3
install python36 on centos


### airflow
安装apache-airflow，主要是配置好airflow webserver和 airflow scheduler 这两个服务。


### elasticsearch
安装elasticsearch


### postgresql
show how to install postgresql


### mongodb
show how to install mongodb

### nginx
nginx的配置不是一两句话的事，一个初步的配置过程就是在 /etc/nginx 下
- 新建 sites-available 和 sites-enabled 这两个文件夹，然后在 sites-available 下面新建 you_web.conf 文件，本项目给出了一个模板，更多信息请参看 [这篇文章的介绍](https://docs.cdwanze.work/articles/nginx-web-server.html)

```
sudo ln -s /etc/nginx/sites-available/cdwanze.work /etc/nginx/sites-enabled/cdwanze.work
```

### apache
apache从零开始编译到django相关配置等，可做参考，默认不开启。

## group_var 详解

- debug : 开启debug信息

- user: 用户
- group： 用户群


- user_root : 用户的家目录
- project_root: 项目的根目录，默认是用户的家目录下的project文件夹
