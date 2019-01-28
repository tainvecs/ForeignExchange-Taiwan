

import argparse
import sys
import multiprocessing
from multiprocessing import Pool

import re
import json

import time
from datetime import datetime

import smtplib
import email.utils
from email.mime.text import MIMEText

from model.FX_Spider_TW import FX_Spider_TW

DEBUG_MODE = True

BANK_CRAWLER_PROCESSES = multiprocessing.cpu_count()
BANK_TABLE_PATH = 'local:/spider_code/res/bank_table.json'
CURRENCY2ID = 'local:/spider_code/res/currency2id.json'

if sys.platform == 'linux':
    CHROME_DRIVER_PATH = '/spider_code/bin/chromedriver_2.45_linux64'
elif sys.platform == 'darwin':
    CHROME_DRIVER_PATH = '/spider_code/bin/chromedriver_2.45_mac64'

DEFAULT_RETRY = 3
DEFAULT_DELAY = 1


class ResultCollector():

    def __init__(self):
        self.result = []
        self.error_flag = False
        self.error_msg = set()

    def update_result(self, val):
        self.result.append(val)

    def record_error(self, error_msg):
        self.error_flag = True
        self.error_msg.add(str(error_msg))
        print (error_msg)


def ParseArgs():

    parser = argparse.ArgumentParser()

    parser.add_argument('--bank_table')
    parser.add_argument('--processes')
    parser.add_argument('--chrome_driver')
    parser.add_argument('--currency2id')
    parser.add_argument('--retry')
    parser.add_argument('--delay')
    parser.add_argument('--debug')
    parser.add_argument('--email_config')
    parser.add_argument('--mariadb_config')
    parser.add_argument('--out_type')
    parser.add_argument('--out_file')

    args = parser.parse_args()

    if not args.bank_table:
        args.bank_table = BANK_TABLE_PATH
    match = re.match(r'([^:]*):(.*)', args.bank_table.strip())
    args.bank_table = __load_bank_info(source=match.group(2), source_type=match.group(1))

    if args.processes:
        args.processes = int(args.processes)
    else:
        args.processes = BANK_CRAWLER_PROCESSES

    if not args.chrome_driver:
        args.chrome_driver = CHROME_DRIVER_PATH

    if not args.currency2id:
        args.currency2id = CURRENCY2ID
    match = re.match(r'([^:]*):(.*)', args.currency2id.strip())
    args.currency2id = __load_fx_alias(source=match.group(2), source_type=match.group(1))


    if args.retry:
        args.retry = int(args.retry)
    else:
        args.retry = DEFAULT_RETRY

    if args.delay:
        args.delay = int(args.delay)
    else:
        args.delay = DEFAULT_DELAY

    if args.debug:
        if args.debug.strip() in ['True', 'true', 'TRUE', 'T', 't', 'Yes', 'yes', 'YES', 'Y', 'y']:
            args.debug = True
        else:
            args.debug = False
    else:
        args.debug = DEBUG_MODE


    if args.debug:

        print ("################## Arguments ##################")

        args_dict = vars(args)
        for key in args_dict:
            print ( "\t{}: {}".format(key, args_dict[key]) )

        print ("###############################################")

    return args


def __load_bank_info(source, source_type='local'):

    if source_type == 'local':
        with open(source, 'r') as in_file:
            bank_info = json.load(in_file)

    return bank_info

def __load_fx_alias(source, source_type='local'):

    if source_type == 'local':
        with open(source, 'r') as in_file:
            fx_alias = json.load(in_file)

    return fx_alias


def StartBankCrawlersMultiprocessing(args, bank_table_keys, processes, result_collector):

    pool = Pool(processes=processes)

    for bank_id in bank_table_keys:
        pool.apply_async( func=CrawlBankFx, args=[args, args.bank_table[bank_id]],
            callback=result_collector.update_result, error_callback=result_collector.record_error)

    pool.close()
    pool.join()


def CrawlBankFx(args, bank_table_dict):

    if args.debug:
        print (bank_table_dict['bank_id'], 'start')

    # create spider
    fx_spider_tw = FX_Spider_TW(currency2id=args.currency2id, chrome_driver_path=args.chrome_driver, chrome_options=None, debug=args.debug)

    # get html
    page_source = fx_spider_tw.SeleniumOpenUrl(url=bank_table_dict['start_link'],
        click_xpaths=bank_table_dict['click_xpaths'], delay=args.delay)

    # parse html
    parsed_fx_dict = fx_spider_tw.ParseBankFX(
        page_source, bank_table_dict['bank_id'], bank_table_dict['last_updated_xpath'], bank_table_dict['fx_table_xpath'])

    # save to database
    if args.mariadb_config:
        fx_spider_tw.MariaDBSave(mariadb_config_path=args.mariadb_config, parsed_fx_dict=parsed_fx_dict)

    # close Selenium chrome browser and Database Connection
    fx_spider_tw.Close()

    if args.debug:
        print (parsed_fx_dict)
        print (bank_table_dict['bank_id'], 'finish')

    return parsed_fx_dict


def ErrorHandling(args, result_collector, email_config=None):

    if args.debug:
        print ("################## Start Error Handling ##################")

    retry = args.retry

    while(retry > 0 and result_collector.error_flag):

        if args.debug:
            print ("################## Error Handling Retry {} ##################".format(args.retry-retry+1))

        time.sleep(args.delay)
        error_set = set( args.bank_table.keys() ) - set( [ rst['bank_id'] for rst in result_collector.result ] )

        result_collector.error_flag = False
        StartBankCrawlersMultiprocessing(args, error_set, min(len(error_set), args.processes), result_collector)

        retry -= 1

    if email_config and result_collector.error_flag:

        error_set = set( args.bank_table.keys() ) - set( [ rst['bank_id'] for rst in result_collector.result ] )
        error_time_stamp = time_str = datetime.today().strftime("%Y-%m-%d %H:%M")
        error_bank_id_str = ", ".join(list(error_set))
        error_msg_str = ", ".join( list(result_collector.error_msg) )

        __email_report_error(email_config, error_time_stamp, error_bank_id_str, error_msg_str)


def __email_report_error(email_config, error_time_stamp, error_bank_id_str, error_msg_str):

    # smtp login
    smtp = smtplib.SMTP("smtp.gmail.com", 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.login (email_config['from_email'], email_config['password'])

    # create email
    msg = MIMEText('Time: {}\nError Bank_id: {}\nError Message: {}'.format( error_time_stamp, error_bank_id_str, error_msg_str ))
    msg['From'] = email.utils.formataddr((email_config['from_user'], email_config['from_email']))
    msg['To'] = email.utils.formataddr((email_config['to_user'], email_config['to_email']))

    if email_config['subject']:
        msg['Subject'] = email_config['subject']
    else:
        msg['Subject'] = 'FX_Spider_TW Crawling Error Report'

    # send email
    try:
        smtp.sendmail(email_config['from_email'], [ email_config['to_email'] ], msg.as_string())
        if args.debug:
            print ("################## Error report was emailed to {} ##################".format(email_config['to_email']))
    finally:
        smtp.quit()
        return False

    return True


def Output(args, result_list):

    if args.out_file:

        if args.out_type == 'json':
            with open(args.out_file, 'a') as out_file:
                out_file.write(json.dumps(result_list, indent=4, sort_keys=False, ensure_ascii=False))

        elif args.out_type == 'json_lines':
            with open(args.out_file, 'a') as out_file:
                for result in result_list:
                    out_file.write( json.dumps(result, ensure_ascii=False) + '\n')

    elif args.out_type == 'print':
        for result in result_list:
            print (result, '\n')

    elif args.out_type == 'print_pretty':
        for result in result_list:
            print (json.dumps(result, indent=4, sort_keys=False, ensure_ascii=False))


if __name__ == '__main__':


    # parse arguments and load data
    args = ParseArgs()

    # multiprocessing Bank_FX_TW crawling
    result_collector = ResultCollector()
    StartBankCrawlersMultiprocessing(args=args, bank_table_keys=args.bank_table.keys(),
        processes=min(args.processes, len(args.bank_table.keys())), result_collector=result_collector)

    # error handling
    if result_collector.error_flag:

        if args.email_config:
            with open(args.email_config, 'r') as in_file:
                email_config = json.load(in_file)
        else:
            email_config = None

        ErrorHandling(args, result_collector, email_config=email_config)

    # output
    Output(args, result_collector.result)
