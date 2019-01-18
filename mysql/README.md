## Environment
* MariaDB 8.0


## Maintainer Info
* Chin-Ho, Lin
* <tainvecs@gmail.com>


## Run Docker Container

```bash
docker run -it --name "container_name" -p 3306:3306 -v mysql_code:/mysql_code tainvecs/fx_tw-mysql:0.0.2
```


## Starting MySQL Server
* the container runs the script /mysql_code/start_mysql.sh
* /mysql_code/start_mysql.sh runs the following command as default
* root default password: "root_pwd"

```bash
if [ -f /mysql_code/my.cnf ]; then
    cp /mysql_code/my.cnf /etc/my.cnf
fi

service mysql start
mysql -u root -p
```

* run the following command to start a closed container

```bash
docker start -ai "container_name"
```


## Execute /bin/bash command in the Container
* press ^PQ to detach from a started container
* run the following command

```bash
docker exec -it "container_name" /bin/bash
```


## Change Root Password

```sql
SET PASSWORD FOR 'root'@'host_name' = PASSWORD('new_root_password');
flush privileges;
```


## Create New User and Grant All Privileges

```sql
CREATE USER 'user_name'@'host_name' IDENTIFIED BY 'new_user_password';
GRANT ALL PRIVILEGES ON *.* TO 'user_name'@'host_name';
```
