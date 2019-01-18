## Environment
* Ubuntu 18.04
* Python 3.6
* Selenium 3.141.0
* chrome-browser 71.0.3578.98-0
* chromedriver 2.45


## Maintainer Info
* Chin-Ho, Lin
* <tainvecs@gmail.com>


## Run Docker Container

```
docker run -it --name "container_name" -v spider_code:/spider_code tainvecs/fx_tw-crawler
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

```
python3 crawler.py --args_option_1 args_1, ..., --args_option_n args_n
```
