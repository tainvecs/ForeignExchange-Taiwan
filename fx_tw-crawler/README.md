## Environment
* Ubuntu 18.04
* Python 3.6
* Selenium 3.141.0
* chrome-browser 71.0.3578.98-0
* chromedriver 2.45


## Maintainer Info
* Chin-Ho, Lin
* <tainvecs@gmail.com>
* [GitLab](https://gitlab.com/tainvecs/foreignexchange-taiwan/)


## Outline
* [/fx_tw-crawler](https://github.com/tainvecs/ForeignExchange-Taiwan/tree/master/fx_tw-crawler/#fx_tw-crawler)
    + crawler.py
* [/fx_tw-crawler/src](https://github.com/tainvecs/ForeignExchange-Taiwan/tree/master/fx_tw-crawler/#fx_tw-crawlersrc)
    + init-mariadb.py
    + update-bank_table_fx_trade.py
* [/fx_tw-crawler/res](https://github.com/tainvecs/ForeignExchange-Taiwan/tree/master/fx_tw-crawler/#fx_tw-crawlerres)
    + mariadb.config
    + email.config
* [/fx_tw-crawler/schedule](https://github.com/tainvecs/ForeignExchange-Taiwan/tree/master/fx_tw-crawler/#fx_tw-crawlerschedule)
    + schedule_start.sh
    + schedule.crontab
    + schedule.sh
* [Run a Foreign Exchange Spider Container](https://github.com/tainvecs/ForeignExchange-Taiwan/tree/master/fx_tw-crawler/#run-a-foreign-exchange-spider-container)
    + Docker Network and Docker Volume
    + Create and Run a Foreign Exchange Spider Container
    + Connect to a MariaDB Container


## /fx_tw-crawler
* **crawler.py**
    + The foreign exchange web crawler of banks in Taiwan
    + **--bank_table** (str)
        + Path to bank table
    	+ Format: \"source_type:source_path\"
            + \"source_type\": currently only supports \"local\"
            + \"source_path\": \"/path/to/bank_table_file\"
        + Default: \"local:/spider_code/res/bank_table.json\"
    + **--processes** (int)
    	+ Number of processes
    	+ Default: the number of processors on the computer
    + **--chrome_driver** (str)
    	+ Path to chrome driver
    	+ Format: \"/path/to/chromedriver_binary_file\"
        + Default: \"/spider_code/bin/chromedriver_2.45_linux64\"
    	+ The binary file is also at \"/usr/local/bin/chromedriver\"
    + **--currency2id** (str)
    	+ Path to currency alias dictionary json file
    	+ Format: \"source_type:source_path\"
            + \"source_type\": currently only supports \"local\"
            + \"source_path\": \"/path/to/bank_table_file\"
        + Default: \"local:/spider_code/res/currency2id.json\"
    + **--retry** (int)
    	+ The numbers of times to retry if error encountered
    	+ Default: 3 times
    + **--delay** (int)
    	+ Delay seconds before retry or getting page source after getting url
    	+ Default: 1 second
    + **--debug** (bool)
    	+ Print out debug messages
    	+ Default: True
    + **--email_config** (str)
    	+ Email config file for sending error report
    	+ Example config file is at \"/spider_code/res/email.config\"
    	+ Currently tested and supports gamil
    	+ If not specified, the error report will not be emailed.
    + **--mariadb_config** (str)
    	+ Config file for connecting MariaDB that saves crawled data
    	+ Example config file is at \"/spider_code/res/mariadb.config\"
    	+ If not specified, crawled data will not be saved to MariaDB.
    + **--out_file** (str)
    	+ Output file path
    + **--out_type** (str)
    	+ Output type
    	+ Options: \"json\", \"json_lines\", \"print\" and \"print_pretty\"
            + \"json\" and \"json_lines\" will be ignore if **--out_file** is not specified.
            + \"print\" and \"print_pretty\" will be ignore if **--out_file** is specified.


## /fx_tw-crawler/src
* **init-mariadb.py**
    + Create the database and tables for saving crawled foreign exchange data
    + **--mariadb_config** (str)
        + Config file for connecting mariadb that saves crawled data
    + **--mariadb_init_template** (str)
        + The template of mysql command that create tables
        + Default: \"/spider_code/res/mariadb_init_template.json\"
    + **--bank_table** (str)
        + Path to bank table
* **update-bank_table_fx_trade.py**
    + Update the ***fx_trade*** field of local bank_table json file
    + **--bank_fx_file** (str)
        + The output json file of the foreign exchange Taiwan spider
    + **--bank_table** (str)
        + The target \"bank_table\" file to update
    + **--out_file** (str)
        + Updated \"bank_table\" file


## /fx_tw-crawler/res
* **mariadb.config**
    + MariaDB config file for connecting MariaDB that saves crawled data
	+ Example config file is at \"/spider_code/res/mariadb.config\"
* **email.config**
    + Email config file for sending error report of a foreign exchange crawler
    + Example config file is at \"/spider_code/res/email.config\"
* **.gitignore** and **.dockerignore** will ignore files with '.private' at the end of filename. You may add '.private' to the end of the filename of your private key or config files to avoid git keeping track of them. Also, remember to edit filenames in commands and **schedule.sh**.


## /fx_tw-crawler/schedule
* **schedule_start.sh**
    + Generate a new crontab schedule file **schedule.crontab**
    + Remove old and start the new generated crontab schedule
* **schedule.crontab**
	+ Start a schedule that runs the script **schedule.sh**
	+ The schedules run the script every ten minute from 09:00 to 18:00 everyday.
* **schedule.sh**
	+ Run a foreign exchange crawler
	+ Output stdin and stderr to a log file named with timestamp in \"/spider_code/log/\"
	+ Dave crawled data to MariaDB and \"/spider_code/output/\"
	+ Email an error report to the specified email address in email config


## Run a Foreign Exchange Spider Container
* **Docker Network and Docker Volume**
    + Create the Docker Network for Foreign Exchange Spiders and MariaDB Containers
        + ```bash
            docker network create "network_name"
          ```
    + Create the Shared Volume for the FX Spider Code
        + ```bash
            docker volume create "fx_volume_name"
          ```
* **Create and Run a Foreign Exchange Spider Container**
    + ```bash
        docker run \
            -it \
            --name "container_name" \
            --network "network_name" \
            -v "fx_volume_name":/spider_code \
            tainvecs/fx_tw-crawler
      ```
    + \"container_name\", \"network_name\", \"fx_volume_name\"
* **Connect to a MariaDB Container**
    + ```python
        import pymysql
        conn_mysql = ( pymysql.connect(host = "host_name", port = 3306, user = "user_name", password = "user_password", charset="utf8") )
      ```
    + \"host_name\"
	   + The **container name** or the **ip address** of the MariaDB container that connects to the spider with the docker network
       + The **ip address** of the MariaDB container can be look up by docker inspect.
    + \"user_name\", \"user_password\"
* **Connect to PostgreSQL** \(PostgreSQL is not supported yet\)
    + ```python
        import psycopg2
        conn_pg = ( psycopg2.connect(host = "host_name", port = 5432, user = "user_name", password = "user_password") )
        conn_pg.set_client_encoding('UTF8')
      ```
    + \"host_name\"
	   + The **container name** or the **ip address** of the PostgreSQL container that connects to the spider with the docker network
       + The **ip address** of the PostgreSQL container can be look up by docker inspect.
