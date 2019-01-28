
# crontab will set locale to ascii, thus set locale to utf8
export LANG=en_US.UTF-8
export LANGUAGE=en_US.UTF-8
export LC_ALL=en_US.UTF-8


CRAWLER_PATH=/spider_code/crawler.py
CRAWLER_LOG_PATH='/spider_code/log/'$(TZ=Asia/Taipei date +"%Y_%m_%d_%H_%M")'.log'

RES_DIR=/spider_code/res/
BIN_DIR=/spider_code/bin/
OUT_DIR=/spider_code/output/

BANK_TABLE='local:'$RES_DIR'bank_table.json'
FX_ALIAS='local:'$RES_DIR'currency2id.json'
EMAIL_CONFIG=$RES_DIR'email.config'
MARIADB_CONFIG=$RES_DIR'mariadb.config'
CHROME_DRIVER=$BIN_DIR'chromedriver_2.45_linux64'
OUT_PATH=$OUT_DIR'bank_data-'$(TZ=Asia/Taipei date +"%Y_%m_%d_%H_%M")'.json'


echo "######################################" >> $CRAWLER_LOG_PATH
echo $(TZ=Asia/Taipei date +"%Y_%m_%d_%H_%M") >> $CRAWLER_LOG_PATH
echo "######################################" >> $CRAWLER_LOG_PATH

python3 $CRAWLER_PATH \
    --bank_table $BANK_TABLE \
    --processes 8 \
    --chrome_driver $CHROME_DRIVER \
    --currency2id $FX_ALIAS \
    --retry 5  \
    --delay 1 \
    --debug True \
    --email_config $EMAIL_CONFIG \
    --mariadb_config $MARIADB_CONFIG \
    --out_type json_lines \
    --out_file $OUT_PATH >> $CRAWLER_LOG_PATH 2>&1
