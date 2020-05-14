# TeamPlatform

实验室管理协作平台，实现对实验室的管理及学生团队内部的协作。

后端：Flask、MySQL

前端：Bootstrap4、jQuery、Layer

---

部署步骤：

* 安装Nginx，建立virtualenv，并在虚拟环境中安装uWSGI.
* 还原环境`pip install -r requirements.txt`.
* 根据实际情况修改uwsgi.ini，并启动uwsgi，创建socket文件.
* 建立软连接nginx.conf到/etc/nginx/sites-enabled/，根据实际情况修改nginx.conf，检查配置文件`/usr/sbin/nginx -t`，重新加载配置文件`/usr/sbin/nginx -s reload`.

