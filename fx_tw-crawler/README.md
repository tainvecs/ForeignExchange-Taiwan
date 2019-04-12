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
* [/fx_tw-crawler](https://gitlab.com/tainvecs/foreignexchange-taiwan/tree/master/fx_tw-crawler/#fx_tw-crawler)
    + crawler.py
* [/fx_tw-crawler/src](https://gitlab.com/tainvecs/foreignexchange-taiwan/tree/master/fx_tw-crawler/#fx_tw-crawlersrc)
    + init-mariadb.py
    + update-bank_table_fx_trade.py
* [/fx_tw-crawler/res](https://gitlab.com/tainvecs/foreignexchange-taiwan/tree/master/fx_tw-crawler/#fx_tw-crawlerres)
    + mariadb config
    + email config
* [/fx_tw-crawler/schedule](https://gitlab.com/tainvecs/foreignexchange-taiwan/tree/master/fx_tw-crawler/#fx_tw-crawlerschedule)
    + schedule_start.sh
    + schedule.crontab
    + schedule.sh
* [Run a Foreign Exchange Spider Container](https://gitlab.com/tainvecs/foreignexchange-taiwan/tree/master/fx_tw-crawler/#run-a-foreign-exchange-spider-container)
    + Docker Network and Docker Volume
    + Run a FX Spider Container
    + Connect to a MariaDB Container


## /fx_tw-crawler
* **crawler.py**
    + foreign exchange web crawler of banks in Taiwan
    + **--bank_table**
        + path to bank table
    	+ default: "local:/spider_code/res/bank_table.json"
    	+ format: "source_type:source_path"
    	+ source_type: currently only support "local"
    	+ source_path: /path/to/bank_table_file
    + **--processes**
    	+ number of process
    	+ default: number of processors on the computer
    + **--chrome_driver**
    	+ path to chrome driver
    	+ default: "/spider_code/bin/chromedriver_2.45_linux64"
    	+ format: /path/to/chromedriver_binary_file
    	+ binary file is also at "/usr/local/bin/chromedriver"
    + **--currency2id**
    	+ path to currency alias dictionary json file
    	+ default: "local:/spider_code/res/currency2id.json"
    	+ format: "source_type:source_path"
    	+ source_type: currently only support "local"
    	+ source_path: /path/to/bank_table_file
    + **--retry**
    	+ times of retry if error encountered
    	+ default: 3 times
    + **--delay**
    	+ seconds of delay before retry or getting page source after get url
    	+ default: 1 second
    + **--debug**
    	+ print out debug messages
    	+ default: True
    + **--email_config**
    	+ email config file for sending error report
    	+ example config file is at "/spider_code/res/email.config"
    	+ currently tested and supports gamil
    	+ if not specified, error reported will not be emailed
    + **--mariadb_config**
    	+ config file for connecting mariadb that saves crawled data
    	+ example config file is at "/spider_code/res/mariadb.config"
    	+ if not specified, crawled data will not be saved to mariadb
    + **--out_file**
    	+ output file path
    + **--out_type**
    	+ output type
    	+ including "json", "json_lines", "print" and "print_pretty"
    	+ "json" and "json_lines" will be ignore if **--out_file** not specified
    	+ "print" and "print_pretty" will be ignore if **--out_file** specified


## /fx_tw-crawler/src
* **init-mariadb.py**
    + create the database and tables for saving crawled fx data
    + **--mariadb_config**
        + config file for connecting mariadb that saves crawled data
    + **--mariadb_init_template**
        + default: /spider_code/res/mariadb_init_template.json
        + template of mysql command that create tables
    + **--bank_table**
        + path to bank table
* **update-bank_table_fx_trade.py**
    + update the ***fx_trade*** field of local bank_table json file
    + **--bank_fx_file**
        + the output json file of the FX Taiwan Spider
    + **--bank_table**
        + the target bank_table file to update
    + **--out_file**
        + updated bank_table file


## /fx_tw-crawler/res
* **mariadb config**
    + mariadb config file for connecting mariadb that saves crawled data
	+ default config file is at "/spider_code/res/mariadb.config"
* **email config**
    + email config file for sending error report of a fx crawler
    + default config file is at "/spider_code/res/email.config"
* **.gitignore** and **.dockerignore** will ignore files with '.private' at the end of filename. You may add '.private' to the end of the filename of your private key or config files to avoid git keeping track of them. Also, remember to edit filenames in the commands and **schedule.sh**.


## /fx_tw-crawler/schedule
* **schedule_start.sh**
    + generate a new crontab schedule file **schedule.crontab**
    + remove old and start the new generated crontab schedule
* **schedule.crontab**
	+ start a schedule that run the script **schedule.sh**
	+ the schedule run the script every ten minute from 09:00 to 18:00 everyday
* **schedule.sh**
	+ run a FX Taiwan Spider
	+ output stdin and stderr to a log file named with timestamp in /spider_code/log/
	+ save crawled data to mariadb and /spider_code/output/
	+ email an error report to the specified email address in email config


## Run a Foreign Exchange Spider Container
* **Docker Network and Docker Volume**
    + the Docker Network for FX Spiders and Database Containers
        + ```bash
            docker network create "network_name"
          ```
    + the Shared Volume for the FX Spider Code
        + ```bash
            docker volume create "fx_volume_name"
          ```
* **Run a FX Spider Container**
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
    + ```Python
        import pymysql
        conn_mysql = ( pymysql.connect(host = "host_name", port = 3306, user = "user_name", password = "user_password", charset="utf8") )
      ```
    + \"host_name\"
	   + The **container name** or the **ip address** of the mariadb container that connects to the spider with the docker network.
       + The **ip address** of the mariadb container can be look up by docker inspect.
    + \"user_name\", \"user_password\"
* **Connect to PostgreSQL** (PostgreSQL is not supported yet)
    + ```Python
        import psycopg2
        conn_pg = ( psycopg2.connect(host = "host_name", port = 5432, user = "user_name", password = "user_password") )
        conn_pg.set_client_encoding('UTF8')
      ```
    + \"host_name\"
	   + The **container name** or the **ip address** of the postgresql container that connects to the spider with the docker network.
       + The **ip address** of the postgresql container can be look up by docker inspect.

