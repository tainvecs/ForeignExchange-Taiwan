## Environment
* Ubuntu 18.04
* Python 3.6
* Selenium 3.141.0
* chrome-browser 71.0.3578.98-0
* chromedriver 2.45


## Maintainer Info
* Chin-Ho, Lin
* <tainvecs@gmail.com>


## Create a Docker Network and a Shared Volume

* the Docker Network for FX Spiders and Database Containers

```bash
docker network create "network_name"
```

* the Shared Volume for the FX Spider Code

```bash
docker volume create "fx_volume_name"
docker volume create "db-my_volume_name"
docker volume create "db-pg_volume_name"
```


## Create and Run a Spider Container

```bash
docker run -it --name "container_name" --network "network_name" \
    -v "fx_volume_name":/spider_code tainvecs/fx_tw-crawler:2.0
```


## Run a FX Taiwan Spider

* **--bank_table**
	- path to bank table
	- default: "local:/spider_code/res/bank_table.json"
	- format: "source_type:source_path"
	- source_type: currently only support "local"
	- source_path: /path/to/bank_table_file
* **--processes**
	- number of process
	- default: number of processors on the computer
* **--chrome_driver**
	- path to chrome driver
	- default: "/spider_code/bin/chromedriver_2.45_linux64"
	- format: /path/to/chromedriver_binary_file
	- binary file is also at "/usr/local/bin/chromedriver"
* **--currency2id**
	- path to currency alias dictionary json file
	- default: "local:/spider_code/res/currency2id.json"
	- format: "source_type:source_path"
	- source_type: currently only support "local"
	- source_path: /path/to/bank_table_file
* **--retry**
	- times of retry if error encountered
	- default: 3 times
* **--delay**
	- seconds of delay before retry or getting page source after get url
	- default: 1 second
* **--debug**
	- print out debug messages
	- default: True
* **--email_config**
	- email config file for sending error report
	- example config file is at "/spider_code/res/email.config"
	- currently tested and supports gamil
	- if not specified, error reported will not be emailed
* **--mariadb_config**
	- config file for connecting mariadb that saves crawled data
	- example config file is at "/spider_code/res/mariadb.config"
	- if not specified, crawled data will not be saved to mariadb
* **--out_file**
	- output file path
* **--out_type**
	- output type
	- including "json", "json_lines", "print" and "print_pretty"
	- "json" and "json_lines" will be ignore if **--out_file** not specified
	- "print" and "print_pretty" will be ignore if **--out_file** specified


```bash
python3 crawler.py --args_option_1 args_1, ..., --args_option_n args_n
```


## Schedule

* **schedule_start.sh**
	- generate a new crontab schedule file **schedule.crontab**
	- remove old and start the new generated crontab schedule
	- default: /spider_code/schedule/schedule_start.sh
* **schedule.crontab**
	- start a schedule that run the script **schedule.sh**
	- default: /spider_code/schedule/schedule.crontab
	- the schedule run the script every ten minute from 09:00 to 18:00 everyday
* **schedule.sh**
	- run a FX Taiwan Spider
	- default: /spider_code/schedule/schedule.sh
	- output stdin and stderr to a log file named with timestamp in /spider_code/log/
	- save crawled data to mariadb and /spider_code/output/
	- email an error report to the specified email address in email config


## Create and Run a MariaDB container

* **MYSQL_ROOT_PASSWORD**
	- default password for root (set to "root" in the example command)
* **Other Parameters**
	- MYSQL_USER
	- MYSQL_PASSWORD

```bash
docker run -d --name "container_name" --network "network_name" \
    -v "db-my_volume_name":/mariadb_code -e MYSQL_ROOT_PASSWORD=root tainvecs/fx_tw-mariadb:1.0
```


## Connect to MySQL

* **host_name**
	- The **container name** or the **ip address** of the postgresql container that connects to the spider with the docker network.
* The **ip address** of the postgresql container can be look up by docker inspect.
* **user_name** and **user_password** are both be set to **"root"** in this example.

```Python
import pymysql
conn_mysql = ( pymysql.connect(host = "host_name", port = 3306, user = "user_name", password = "user_password", charset="utf8") )
```


## Initialize the MariaDB

* **init-mariadb.py**
    - create the database and tables for saving crawled fx data
    - **--mariadb_config**
    	+ config file for connecting mariadb that saves crawled data
    - **--mariadb_init_template**
        + default: /spider_code/res/mariadb_init_template.json
        + template of mysql command that create tables
    - **--bank_table**
    	+ path to bank table
* **update-bank_table_fx_trade.py**
	- update the ***fx_trade*** field of local bank_table json file
	- **--bank_fx_file**
		+ the output json file of the FX Taiwan Spider
	- **--bank_table**
		+ the target bank_table file to update
	- **--out_file**
		+ updated bank_table file


## Create and Run a PostgreSQL container (PostgreSQL is not Supported yet)

```bash
docker run -d --name "container_name" --network "network_name" \
    -v "db-pg_volume_name":/postgres_code -e POSTGRES_USER=root -e POSTGRES_PASSWORD=root tainvecs/fx_tw-postgres:0.0.3
```


## Connect to PostgreSQL (PostgreSQL is not Supported yet)

* **host_name**
	- The **container name** or the **ip address** of the postgresql container that connects to the spider with the docker network.
* The **ip address** of the postgresql container can be look up by docker inspect.
* **user_name** and **user_password** are both be set to **"root"** in this example.

```Python
import psycopg2
conn_pg = ( psycopg2.connect(host = "host_name", port = 5432, user = "user_name", password = "user_password") )
conn_pg.set_client_encoding('UTF8')
```
