## Environment
* Ubuntu 18.04
* MariaDB 10.3


## Maintainer Info
* Chin-Ho, Lin
* <tainvecs@gmail.com>


## Run Docker Container

```
docker run -it --name "container_name" tainvecs/fx_tw-mysql
```


## Starting MySQL Server

```
service mysql start
```


## Login Root Account
* root default password: "root_pwd"

```
mysql -u root -p
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
