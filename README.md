## Environment
* Ubuntu 18.04
* Python 3.6
* Docker 18.09.4
* docker-compose 1.24.0
* Selenium 3.141.0
* chrome-browser 71.0.3578.98-0
* chromedriver 2.45
* MariaDB 10.3


## Maintainer Info
* Chin-Ho, Lin
* <tainvecs@gmail.com>
* [GitLab](https://gitlab.com/tainvecs/foreignexchange-taiwan/)


## Overview
This project provides a foreign exchange spider of [34](https://gitlab.com/tainvecs/foreignexchange-taiwan/tree/master/fx_tw-crawler/res/banks.md) banks in Taiwan. The spider crawls latest foreign exchange data from the websites of banks and save them to json files or a MariaDB database. The project environment can be build and set up with docker-compose. The project also supports crontab schedule and emailing error report for foreign exchange spiders. 


## Outline
* [Structure](https://gitlab.com/tainvecs/foreignexchange-taiwan/#structure)
    + **Docker Image**
        + fx_tw-crawler
        + fx_tw-mariadb
    + **Docker Container**
        + fx
        + db-my
    + **Shared Volume**
        + spider_code
        + mysql_data
        + mysql_code
    + **Network**
        + db-net
* [Build](https://gitlab.com/tainvecs/foreignexchange-taiwan/#build)
    + **Option 1: Build with Docker Compose**
        + Build Docker Images and Set Up Network and Shared Volumes
        + Start and Run Containers
    + **Option 2: Build with Dockerfile**
        + Docker Images
            + Option 1: Build Docker Images with Dockerfile
            + Option 2: Pull Docker Images from Docker Hub
        + Docker Volume
        + Docker Network
        + Docker Containers
* [Set Up](https://gitlab.com/tainvecs/foreignexchange-taiwan/#set-up)
    + **Set Up MariaDB (Optional)**
    + **Set up Email Config for Sending Error Report (Optional)**
* [Run](https://gitlab.com/tainvecs/foreignexchange-taiwan/#run)
    + **Run a Foreign Exchange Crawler**
    + **Set Up Schedule for Foreign Exchange Crawler (Optional)**


## Structure
* **Docker Image**
    - **fx_tw-crawler**
        + The docker image of spider that crawls the foreign exchange data of banks in Taiwan
    - **fx_tw-mariadb**
        + The docker image of mariadb that saves the crawled data
* **Docker Container**
    - **fx**
        + The container instance of **fx_tw-crawler**
    - **db-my**
        + The container instance of **fx_tw-mariadb**
* **Shared Volume**
    - **spider_code**
        + The share volume for the code of a foreign exchange spider
    - **mysql_data**
        + The share volume of mysql default data directory in a **db-my** container
    - **mysql_code**
        + The share volume for the code of a **db-my** container
* **Network**
    - **db-net**
        + Container network between **fx** and **db-my**


## Build
* **Option 1: Build with Docker Compose**
    + Build Docker Images and Set Up Network and Shared Volumes
        + ```bash
            docker-compose build --no-cache
          ```
    + Start and Run Containers
        + ```bash
            docker-compose up -d
          ```
* **Option 2: Build with Dockerfile**
    + Docker Images
        + Option 1: Build Docker Images with Dockerfile
            + ```bash
                docker build -t tainvecs/fx_tw-crawler --no-cache ./fx_tw-crawler
                docker build -t tainvecs/fx_tw-mariadb --no-cache ./fx_tw-mariadb
              ```
        + Option 2: Pull Docker Images from Docker Hub
            + ```bash
                docker pull tainvecs/fx_tw-crawler
                docekr pull tainvecs/fx_tw-mariadb
              ```
    + Docker Volume
        + ```bash
            docker volume create "spider_code"
            docker volume create "mysql_data"
            docker volume create "mysql_code"
          ```
    + Docker Network
        + ```bash
            docker network create db-net
          ```
    + Docker Containers
        + ```bash
            docker run \
                -itd \
                --name fx \
                --network db-net \
                -v spider_code:/spider_code \
                tainvecs/fx_tw-crawler
            docker run \
                -d \
                --name db-my \
                --network db-net \
                -v mysql_data:/var/lib/mysql \
                -v mysql_code:/mariadb_code \
                -e MYSQL_ROOT_PASSWORD=root \
                tainvecs/fx_tw-mariadb
          ```


## Set Up
+ **Set Up MariaDB (Optional)**
    + Execute **\"/bin/bash\"** Command in **db-my** Container
        + ```bash
            docker exec -it db-my /bin/bash
          ```
    + Connecting to the MySQL Server
        + ```mysql
            mysql -u root -h localhost -P 3306 -p
          ```
    + Change the Root Password
        + ```mysql
            SET PASSWORD FOR 'root'@'locahost' = PASSWORD('new_root_password');
            flush privileges;
          ```
        + \"new_root_password\"
    + Create a New User and Grant All Privileges
        + ```bash
            CREATE USER 'user_name'@'locahost' IDENTIFIED BY 'new_user_password';
            GRANT ALL PRIVILEGES ON *.* TO 'user_name'@'locahost';
          ```
        + \"user_name\", \"new_user_password\"
    + Exit from **db-my** Container
        + ```bash
            exit
          ```
    + Execute **\"/bin/bash\"** Command in **fx** Container
        + ```bash
            docker exec -it fx /bin/bash
          ```
    + Set Up MariaDB Config File **\"/spider_code/res/mariadb.config\"** \([more info](https://gitlab.com/tainvecs/foreignexchange-taiwan/tree/master/fx_tw-crawler#fx_tw-crawlerres)\)
        + ```json
            {
                "mariadb_host": "db-my",
                "mariadb_port": 3306,
                "mariadb_user": "user_name",
                "mariadb_password": "user_password",
                "mariadb_database": "fx_tw",
                "mariadb_charset": "utf8"
            }
          ```
        + \"user_name\", \"user_password\"
    + Initailize the Database for Saving Crawled Data \([more info](https://gitlab.com/tainvecs/foreignexchange-taiwan/tree/master/fx_tw-crawler#fx_tw-crawlersrc)\)
        + ```bash
            python3 /spider_code/src/init-mariadb.py \
                --mariadb_config /spider_code/res/mariadb.config \
                --mariadb_init_template /spider_code/res/mariadb_init_template.json \
                --bank_table /spider_code/res/bank_table.json
          ```
    + Exit from **fx** Container
        + ```bash
            exit
          ```
+ **Set up Email Config for Sending Error Report (Optional)**
    + Gmail APP passwords should be generated in advance
    + Execute **\"/bin/bash\"** Command in **fx** Container
        + ```bash
            docker exec -it fx /bin/bash
          ```
    + Set Up MariaDB Config File **\"/spider_code/res/mariadb.config\"** \([more info](https://gitlab.com/tainvecs/foreignexchange-taiwan/tree/master/fx_tw-crawler#fx_tw-crawlerres)\)
        + ```json
            {
                "from_user": "username_from",
                "from_email": "email_address_from",
                "password": "email_app_password",
                "to_user": "username_to",
                "to_email": "email_address_to",
                "subject": "subject"
            }
          ```
        + \"email_app_password\"
            + gmail app passwords
        + \"username_from\", \"email_address_from\", \"username_to\", \"email_address_to\", \"subject\"
    + Exit from **fx** Container
        + ```bash
            exit
          ```


## Run
+ **Run a Foreign Exchange Crawler** \([more info](https://gitlab.com/tainvecs/foreignexchange-taiwan/tree/master/fx_tw-crawler#fx_tw-crawler)\)
    + Attach to the **fx** Container
        + ```bash
            docker attach fx
          ```
    + Run a Crawler and Save Crawled Data to a Json File **\"/spider_code/bank-data.json\"**
        + ```bash
            python3 /spider_code/crawler.py \
                --bank_table local:/spider_code/res/bank_table.json \
                --currency2id local:/spider_code/res/currency2id.json \
                --out_file /spider_code/bank-data.json \
                --out_type json_lines
          ```
    + Run a Crawler and Save Crawled Data to MariaDB
        + ```bash
            python3 /spider_code/crawler.py \
                --bank_table local:/spider_code/res/bank_table.json \
                --currency2id local:/spider_code/res/currency2id.json \
                --mariadb_config /spider_code/res/mariadb.config
          ```
    + Run a Crawler that Save Crawled Data to MariaDB and Email an Error Report
        + ```bash
            python3 /spider_code/crawler.py \
                --bank_table local:/spider_code/res/bank_table.json \
                --currency2id local:/spider_code/res/currency2id.json \
                --email_config /spider_code/res/email.config \
                --mariadb_config /spider_code/res/mariadb.config
          ```
    + Detach from the **fx** Container
        + Press Ctrl+p Ctrl+q
+ **Set Up Schedule for Foreign Exchange Crawler (Optional)** \([more info](https://gitlab.com/tainvecs/foreignexchange-taiwan/tree/master/fx_tw-crawler#fx_tw-crawlerschedule)\)
    + Attach to the **fx** Container
        + ```bash
            docker attach fx
          ```
    + Edit the Command of Schedule Crawler
        + **\"/spider_code/schedule/schedule.sh\"**
        + Default scheduled crawler save crawled data to MariaDB and a json file in **\"/spider_code/output/\"**.
        + Default scheduled crawler also use the email_config **\"/spider_code/res/email.config\"** to send error report.
    + Edit the Schedule Task
        + **\"/spider_code/schedule/schedule_start.sh\"**
        + Default schedule task run the crawler every ten minutes from 09:00 to 18:00 everyday.
        + Default schedule task also redirects stdin and stderr to a log file **\"/spider_code/log/crontag.log\"**.
    + Start a Schedule Task for a foreign exchange Crawler
        + ```bash
            bash /spider_code/schedule/schedule_start.sh
          ```
    + Detach from the **fx** Container
        + Press Ctrl+p Ctrl+q

