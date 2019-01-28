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


## Start with Docker Compose

* build docker images and set up network and shared volumes
* **--no-cache**: use no cache

```bash
docker-compose build --no-cache
```

* start and run containers
* **-d**: detch mode

```bash
docker-compose up -d
```

* Docker Images
    - **fx_tw-crawler**
        + The docker image of spiders that crawl foreigner exchange data of Taiwan.
    - **fx_tw-mariadb**
        + The docker image of mariadb that saves the crawled data.
* Docker Container
    - **fx**
        + The container instance of fx_tw-crawler.
    - **db-my**
        + The container instance of fx_tw-mariadb.
* Shared Volume
    - **spider_code**
        + The share volume for the code of a fx spider.
    - **mysql_data**
        + The share volume of mysql default data directory of the db-my container.
    - **mysql_code**
        + The share volume for the code of a db-my container.
* Network
    - **db-net**


## Set up Config Files for Database and Email

* **mariadb config**
    - mariadb config file for connecting mariadb that saves crawled data
	- default config file is at "/spider_code/res/mariadb.config"
* **email config**
    - email config file for sending error report of a fx crawler
    - default config file is at "/spider_code/res/email.config"


## Initialize the Database for Saving Crawled Data

* Execute /bin/bash command for FX Crawler container

```bash
docker exec -it fx /bin/bash
```

* Run **init-mariadb.py** to initialize the database ([more info](https://gitlab.com/tainvecs/foreignexchange-taiwan/blob/master/fx_spider_tw/README.md))
    - **--mariadb_config**
    - **--mariadb_init_template**
    - **--bank_table**

```bash
cd /spider_code/src

python init-mariadb.py \
    --mariadb_config ../res/mariadb.config.private \
    --mariadb_init_template ../res/mariadb_init_template.json \
    --bank_table ../res/bank_table.json
```

## Run a FX Crawler or Set up Schedule for it

* Run a FX Crawler ([more info](https://gitlab.com/tainvecs/foreignexchange-taiwan/blob/master/fx_spider_tw/README.md))
    - **--bank_table**
    - **--processes**
    - **--chrome_driver**
    - **--currency2id**
    - **--retry**
    - **--delay**
    - **--debug**
    - **--email_config**
    - **--mariadb_config**
    - **--out_file**
    - **--out_type**

```bash
cd /spider_code

python crawler.py \
    --bank_table local:/spider_code/res/bank_table.json \
    --processes 8 \
    --chrome_driver /spider_code/bin/chromedriver_2.45_linux64 \
    --currency2id local:/spider_code/res/currency2id.json \
    --retry 5 \
    --delay 1 \
    --debug True \
    --out_file /spider_code/bank-data.json \
    --out_type json_lines \
    --email_config /spider_code/res/email.config.private \
    --mariadb_config /spider_code/res/mariadb.config.private
```

* If an unknown key error occur while inserting crawled data to mariadb, the bank might supports new currency trading. Try to alter the table that named with the bank id and update /spider_code/res/bank_table.json with the following code.

```bash
cd /spider_code/src

python update-bank_table_fx_trade.py \
    --bank_fx_file /spider_code/bank-data.json \
    --bank_table /spider_code/res/bank_table.json \
    --out_file /spider_code/res/bank_table_new.json
```

* Set up Schedule for a FX Crawler ([more info](https://gitlab.com/tainvecs/foreignexchange-taiwan/blob/master/fx_spider_tw/README.md))
    - **schedule_start.sh**
    - **schedule.crontab**
    - **schedule.sh**

```bash
cd /spider_code/schedule

bash schedule_start.sh
```


## Future Work

* Create a new ssh container that able to access the container's code shared volumes **spider_code** and **mysql_code**.
* Imporve error handling of the fx crawler. Currently only retry if web connection fails or not able to crawl the target bank fx data. For instance alter add colume if a bank support tradding new currency.
* Support loading bank_info table and currency2id from mariadb. Currenctly can only be loaded from local.
* Learn and support PostgreSQL.
* Create an interface to retireve data from mariadb.
* Crawl the history fx data.
