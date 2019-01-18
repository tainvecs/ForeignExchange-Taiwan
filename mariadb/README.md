## Environment
* MariaDB 10.3


## Maintainer Info
* Chin-Ho, Lin
* <tainvecs@gmail.com>


## Create a Docker Network for MariaDB Containers

```bash
docker network create "network_name"
```


## Create and Run a MariaDB container

* MYSQL_ROOT_PASSWORD: default password for root (set to "root" in the example command)
* other parameters: MYSQL_USER, MYSQL_PASSWORD

```bash
docker run -d --name "container_name" --network "network_name" \
    -v mariadb_code:/mariadb_code -e MYSQL_ROOT_PASSWORD=root tainvecs/fx_tw-mariadb:0.0.3
```


## Execute /bin/bash Command in a Started Container

* run the following command

```bash
docker exec -it "container_name" /bin/bash
```

* MySQL Command Line Client

```bash
mysql -u "user_name" -h "host_name" -P "port" -p
```


## Change the Root Password

```sql
SET PASSWORD FOR 'root'@'host_name' = PASSWORD('new_root_password');
flush privileges;
```


## Create a New User and Grant All Privileges

```sql
CREATE USER 'user_name'@'host_name' IDENTIFIED BY 'new_user_password';
GRANT ALL PRIVILEGES ON *.* TO 'user_name'@'host_name';
```
