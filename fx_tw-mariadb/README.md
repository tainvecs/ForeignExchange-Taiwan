## Environment
* MariaDB 10.3


## Maintainer Info
* Chin-Ho, Lin
* <tainvecs@gmail.com>
* [GitLab](https://gitlab.com/tainvecs/foreignexchange-taiwan/)


## Outline
* [Run a MariaDB Container for Foreign Exchange Crawler](https://gitlab.com/tainvecs/foreignexchange-taiwan/tree/master/fx_tw-mariadb/#run-a-mariadb-container-for-foreign-exchange-crawler)
    + Docker Network and Docker Volume
    + Run a MariaDB Container
    + Set Up MariaDB


## Run a MariaDB Container for Foreign Exchange Crawler
* **Docker Network and Docker Volume**
    + Create the Docker Network for Foreign Exchange Spiders and MariaDB Containers
        + ```bash
            docker network create "network_name"
          ```
    + Create the Shared Volume for MariaDB Containers
        + ```bash
            docker volume create "volume_name"
          ```
* **Run a MariaDB Container**
    + ```bash
        docker run \
            -d \
            --name "container_name" \
            --network "network_name" \
            -v "volume_name":/mariadb_code \
            -e MYSQL_ROOT_PASSWORD=root \
            tainvecs/fx_tw-mariadb
      ```
    + **MYSQL_ROOT_PASSWORD**
        + Default password for root (set to "root" in the example command)
    + **MYSQL_USER**, **MYSQL_PASSWORD**
    + \"container_name\", \"network_name\", \"volume_name\"

+ **Set Up MariaDB**
    + Execute **\"/bin/bash\"** Command in a MariaDB Container
        + ```bash
            docker exec -it "container_name" /bin/bash
          ```
        + \"container_name\"
    + Connecting to the MySQL Server
        + ```bash
            mysql -u "user_name" -h "host_name" -P "port" -p
          ```
        + \"user_name\", \"host_name\", \"port\"
    + Change the Root Password
        + ```sql
            SET PASSWORD FOR 'root'@'host_name' = PASSWORD('new_root_password');
            flush privileges;
          ```
        + \"host_name\", \"new_root_password\"
    + Create a New User and Grant All Privileges
        + ```sql
            CREATE USER 'user_name'@'host_name' IDENTIFIED BY 'new_user_password';
            GRANT ALL PRIVILEGES ON *.* TO 'user_name'@'host_name';
          ```
        + \"user_name\", \"host_name\", \"new_user_password\"
    + Exit from a MariaDB Container
        + ```bash
            exit
          ```
