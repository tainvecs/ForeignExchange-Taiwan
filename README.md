## Environment
* Ubuntu 18.04
* Python 3.6
* Selenium 3.141.0
* chrome-browser 71.0.3578.98-0
* chromedriver 2.45
* MariaDB 10.3


## Maintainer Info
* Chin-Ho, Lin
* <tainvecs@gmail.com>
* [GitLab](https://gitlab.com/tainvecs/foreignexchange-taiwan/)


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
* [Get Started with Docker Compose](https://gitlab.com/tainvecs/foreignexchange-taiwan/#get-started-with-docker-compose)
    + **Build**
        + Build Docker Images and Set Up Network and Shared Volumes
    + **Set Up**
        + Start and Run Containers
        + Set Up MariaDB
        + Set up Email Config for Sending Error Report (Optional)
    + **Run**
        + Attach to the \"fx\" Container
        + Run a Foreign Exchange Crawler
            + Run a Crawler and Save Crawled Data to a Json File \"/spider_code/bank-data.json\"
            + Run a Crawler and Save Crawled Data to MariaDB
            + Run a Crawler that Save Crawled Data to MariaDB and Email an Error Report
        + Set Up Schedule for Foreign Exchange Crawler
            + Edit the Command of Schedule Crawler
            + Edit the Schedule Task
            + Start a Schedule Task for an Foreign Exchange Crawler
        + Detach from the \"fx\" Container


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


## Get Started with Docker Compose
* **Build**
    + **Build Docker Images and Set Up Network and Shared Volumes**
        + ```bash
            docker-compose build --no-cache
          ```
* **Set Up**
    + **Start and Run Containers**
        + ```bash
            docker-compose up -d
          ```
    + **Set Up MariaDB**
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
            + \"user_name\"
            + \"new_user_password\"
        + Exit from **db-my** Container
            + ```bash
                exit
              ```
        + Execute **\"/bin/bash\"** Command in **fx** Container
            + ```bash
                docker exec -it fx /bin/bash
              ```
        + Set Up MariaDB Config File **\"/spider_code/res/mariadb.config\"**
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
            + \"user_name\"
            + \"user_password\"
        + Initailize the Database for Saving Crawled Data
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
        + Set Up MariaDB Config File **\"/spider_code/res/mariadb.config\"**
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
            + \"username_from\"
            + \"email_address_from\"
            + \"email_app_password\": gmail app passwords
            + \"username_to\"
            + \"email_address_to\"
            + \"subject\"
        + Exit from **fx** Container
            + ```bash
                exit
              ```
* **Run**
    + **Attach to the fx Container**
        + ```bash
            docker attach fx
          ```
    + **Run a Foreign Exchange Crawler**
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
    + **Set Up Schedule for Foreign Exchange Crawler**
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
    + **Detach from the fx Container**
        + Press Ctrl+p Ctrl+q

