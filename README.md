# TeamPlatform

实验室管理协作平台，实现对实验室的管理及学生团队内部的协作。

后端：Flask、MySQL

前端：Bootstrap4、jQuery、Layer

## 功能

实验室管理：事务、活动、座位、资产、人员信息管理；

小组管理：成员、项目、项目需求和缺陷管理；

文件共享：上传文件在不同范围共享、下载文件；

## 演示

演示站点：https://nav.zooter.com.cn

演示账号（可自行创建账号，请勿修改预设账号的密码，谢谢）：

* 管理员：email: zzc1368129224@vip.qq.com password:123123123123
* 学生A：email: zzc1368129224@qq.com password:123123123123
* 学生B：email: 2016052060@test.com password:123123123123

## 部署指南

* 安装Nginx，建立virtualenv，并在虚拟环境中安装uWSGI.
* 还原环境`pip install -r requirements.txt`，根据实际情况修改config.py，执行init_database.sh初始化数据库.
* 根据实际情况修改uwsgi.ini，并启动uwsgi，创建socket文件.
* 建立软连接nginx.conf到/etc/nginx/sites-enabled/，根据实际情况修改nginx.conf，检查配置文件`/usr/sbin/nginx -t`，重新加载配置文件`/usr/sbin/nginx -s reload`.
* uwsgi命令：
  * 启动：uwsgi --ini xxx.ini
  * 重启：uwsgi --reload xxx.pid
  * 停止：uwsgi --stop xxx.pid

