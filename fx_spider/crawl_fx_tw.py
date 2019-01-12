

import argparse
from multiprocessing import Pool
import json

from model.FX_Spider_TW import FX_Spider_TW


BANK_CRAWLER_PROCESSES = None
BANK_TABLE_PATH = './res/bank_table.json'
CHROME_DRIVER_PATH = './bin/chromedriver'
CURRENCY2ID = './res/currency2id.json'


def ParseArgs():

    parser = argparse.ArgumentParser()

    parser.add_argument('--bank_table')
    parser.add_argument('--processes')
    parser.add_argument('--chrome_driver')
    parser.add_argument('--currency2id')
    parser.add_argument('--type')
    parser.add_argument('--out_file')

    args = parser.parse_args()

    if args.processes:
        args.processes = int(args.processes)
    else:
        args.processes = BANK_CRAWLER_PROCESSES

    if not args.bank_table:
         args.bank_table = BANK_TABLE_PATH

    if not args.chrome_driver:
        args.chrome_driver = CHROME_DRIVER_PATH

    if not args.currency2id:
        args.currency2id = CURRENCY2ID
    with open(args.currency2id, 'r') as in_file:
        args.currency2id = json.load(in_file)

    return args


def StartBankCrawlersMultiprocessing(args, bank_table, processes):

    result_list = []

    pool = Pool(processes=processes)
    for bank_id in bank_table:
        result = pool.apply_async( func=CrawlBankFx, args=[args, bank_table[bank_id]] )
        result_list.append(result)

    pool.close()
    pool.join()

    return result_list


def CrawlBankFx(args, bank_table_dict):

    print (bank_table_dict['bank_id'], 'start')

    fx_spider_tw = FX_Spider_TW(currency2id=args.currency2id, chrome_driver_path=args.chrome_driver, chrome_options=None)

    page_source = fx_spider_tw.SeleniumOpenUrl(url=bank_table_dict['start_link'], click_xpaths=bank_table_dict['click_xpaths'], delay=2)
    parsed_fx_dict = fx_spider_tw.ParseBankFX(
        page_source, bank_table_dict['bank_id'], bank_table_dict['last_updated_xpath'], bank_table_dict['fx_table_xpath'])

    fx_spider_tw.Close()

    print (bank_table_dict['bank_id'], 'fininsh')

    return parsed_fx_dict


def Output(args, result_list):

    if args.out_file:

        if args.type == 'json':

            with open(args.out_file, 'a') as out_file:
                result_js_list = [ result.get() for result in result_list ]
                out_file.write(json.dumps(result_js_list, indent=4, sort_keys=False, ensure_ascii=False))

        elif args.type == 'json_lines':

            with open(args.out_file, 'a') as out_file:
                for result in result_list:
                    result_js = result.get()
                    out_file.write( json.dumps(result_js, ensure_ascii=False) + '\n')

    elif args.type == 'print':

        for result in result_list:
            print (result.get(), '\n')

    elif args.type == 'print_pretty':

        for result in result_list:
            print (json.dumps(result.get(), indent=4, sort_keys=False, ensure_ascii=False))


if __name__ == '__main__':

    args = ParseArgs()

    with open(args.bank_table, 'r') as in_file:
        bank_table = json.load(in_file)

    result_list = StartBankCrawlersMultiprocessing(args=args, bank_table=bank_table, processes=args.processes)

    Output(args, result_list)
