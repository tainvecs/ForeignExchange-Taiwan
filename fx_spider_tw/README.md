## Environment
* Ubuntu 18.04
* Python 3.6
* Selenium 3.141.0
* chrome-browser 71.0.3578.98-0
* chromedriver 2.45


## Maintainer Info
* Chin-Ho, Lin
* <tainvecs@gmail.com>


## Create a Docker Network for Spider and Database Containers

```bash
docker network create "network_name"
```


## Create and Run a Spider Container

```bash
docker run -it --name "container_name" --network "network_name" \
    -v spider_code:/spider_code tainvecs/fx_tw-crawler:1.2.1
```


## Run FX Spider Taiwan

* --bank_table: path to bank table json file (default: /res/bank_table.json)
* --processes: number of process (default: number of processers on the computer)
* --chrome_driver: path to chrome driver (default: bin/chromedriver_2.45_linux64, binary also in /usr/local/bin/chromedriver)
* --currency2id: path to currency alias dictionary json file (default: /res/currency2id.json)
* --out_file: output file path
* --type: output type, including json, json_lines, print, and print_pretty
* --retry: times of retry where error encountered (default: 3 times)
* --delay: seconds of delay before retry or getting page source after get url (delay: default 1 second)
* --email: email config file for sending error report (example config file is at /res/email.config)

```bash
python3 crawler.py --args_option_1 args_1, ..., --args_option_n args_n
```


## Create and Run a MariaDB container

* MYSQL_ROOT_PASSWORD: default password for root (set to "root" in the example command)
* other parameters: MYSQL_USER, MYSQL_PASSWORD

```bash
docker run -d --name "container_name" --network "network_name" \
    -v mariadb_code:/mariadb_code -e MYSQL_ROOT_PASSWORD=root tainvecs/fx_tw-mariadb:0.0.3
```


## Connect to MySQL

* host_name: The container name or the ip address of the mariadb container that connects to the spdier with the docker network.
* The ip address of the mariadb container can be look up by docker inspect.
* user_name and user_password can both be set to root in this example.

```Python
import pymysql
conn_mysql = ( pymysql.connect(host = "host_name", port = 3306, user = "user_name", password = "user_password", charset="utf8") )
```


## Create and Run a PostgreSQL container

```bash
docker run -d --name "container_name" --network "network_name" \
    -v postgres_code:/postgres_code -e POSTGRES_USER=root -e POSTGRES_PASSWORD=root tainvecs/fx_tw-postgres:0.0.3
```


## Connect to PostgreSQL

* host_name: The container name or the ip address of the postgresql container that connects to the spdier with the docker network.
* The ip address of the postgresql container can be look up by docker inspect.
* user_name and user_password can both be set to root in this example.

```Python
import psycopg2
conn_pg = ( psycopg2.connect(host = "host_name", port = 5432, user = "user_name", password = "user_password") )
conn_pg.set_client_encoding('UTF8')
```
