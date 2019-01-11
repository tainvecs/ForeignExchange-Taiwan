
import argparse

from multiprocessing import Pool

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import re
from lxml import etree
from bs4 import BeautifulSoup

import json
import time
from datetime import datetime

from collections import defaultdict


BANK_TABLE_PATH = './res/bank_table.json'
BANK_CRAWLER_PROCESSES = None
CHROME_DRIVER_PATH = './bin/chromedriver'

CURRENCY2ID = {
    'US Dollar': 'USD', '美金': 'USD', '美元': 'USD',
    'Chinese Yuan': 'CNY', '人民幣': 'CNY',
    'Australian Dollar': 'AUD', '澳洲幣': 'AUD', '澳幣': 'AUD',
    'Canadian Dollar': 'CAD', '加拿大幣': 'CAD', '加幣': 'CAD',
    'Hong Kong Dollar': 'HKD', '港幣': 'HKD',
    'British Pound': 'GBP', '英鎊': 'GBP',
    'Singapore Dollar': 'SGD', '新加坡幣': 'SGD',
    'South African': 'ZAR', '南非幣': 'ZAR',
    'Swedish Kroner': 'SEK', '瑞典幣': 'SEK',
    'Swiss Franc': 'CHF', '瑞士法郎': 'CHF',
    'Japanese Yen': 'JPY', '日幣': 'JPY', '日圓': 'JPY', '日元': 'JPY',
    'Thai Baht': 'THB', '泰銖': 'THB',
    'Euro': 'EUR', '歐元': 'EUR',
    'New Zealand Dollar': 'NZD', '紐西蘭幣': 'NZD', '紐幣': 'NZD',
}


def ParseArgs():

    parser = argparse.ArgumentParser()

    parser.add_argument('--bank_table')
    parser.add_argument('--processes')
    parser.add_argument('--chrome_driver')
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


def CrawlBankFx(args, bank_table_dict):

    print (bank_table_dict['bank_id'], 'start')

    page_source = SeleniumOpenUrl(
        url=bank_table_dict['start_link'], click_xpaths=bank_table_dict['click_xpaths'], driver_path=args.chrome_driver)
    parsed_fx_dict = ParseBankFX(page_source, bank_table_dict)

    print (bank_table_dict['bank_id'], 'fininsh')

    return parsed_fx_dict


def SeleniumOpenUrl(url, click_xpaths=[], driver_path=CHROME_DRIVER_PATH, options=None, given_browser=None, delay=2):

    if not options:
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1200,1100');
        options.add_argument('user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"')

    if not given_browser:
        browser = webdriver.Chrome(driver_path, options=options)
    else:
        browser = given_browser

    browser.get(url)
    time.sleep(delay)

    for click_xpath in click_xpaths:
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, click_xpath))
            ).click()
        time.sleep(delay)

    page_source = browser.page_source

    if not given_browser:
        browser.quit()

    return page_source


def ParseBankFX(page_source, bank_table_dict):

    xml_tree = etree.HTML(page_source)

    if not (bank_table_dict['last_updated_xpath'] is None):
        time_soup_str = BeautifulSoup(
            etree.tostring(xml_tree.xpath(bank_table_dict['last_updated_xpath'])[0]), features="lxml").get_text().strip()

    if not (bank_table_dict['fx_table_xpath'] is None):
        fx_table_soup = BeautifulSoup( etree.tostring(xml_tree.xpath(bank_table_dict['fx_table_xpath'])[0]), features="lxml" )

    if bank_table_dict['bank_id'] == 'APBKTWTH-806': # 元大

        # last updated
        time_str = __parse_datetime(time_soup_str, year_offset=1911)

        # fx table
        fx_item = {}
        for fx_tr in fx_table_soup.findAll('tr')[1:]:

            cc_tmp, bb_spot, bs_spot, bb_cash, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td')[:5] ]
            cc = re.search(r'.*\((.+?)\).*', cc_tmp).group(1).strip()

            fx_item[cc] = {
                'bb_spot':__format_fx(bb_spot), 'bs_spot':__format_fx(bs_spot),
                'bb_cash':__format_fx(bb_cash), 'bs_cash':__format_fx(bs_cash)
            }

    elif bank_table_dict['bank_id'] == 'BBBKTWTP-118':  # 板信

        # last updated
        time_str = __parse_datetime(time_soup_str, year_offset=1911, re_pattern=r'[^0-9]*(\d+)年[^0-9]*(\d+)[^0-9]*(\d+)日[^0-9]*(\d+):(\d+).*')

        # fx table
        fx_item = {}
        for fx_tr in fx_table_soup.findAll('tr')[1:]:

            cc_tmp, bb_spot, bs_spot, bb_cash, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]
            cc = CURRENCY2ID[cc_tmp]

            fx_item[cc] = {
                'bb_spot':__format_fx(bb_spot), 'bs_spot':__format_fx(bs_spot),
                'bb_cash':__format_fx(bb_cash), 'bs_cash':__format_fx(bs_cash)
            }

    elif bank_table_dict['bank_id'] == 'BKAOTWTK-016':  # 高雄銀行

        # last updated
        time_str = __parse_datetime(time_soup_str, parse_time=False)

        # fx table
        fx_item = {}
        for fx_tr in fx_table_soup.findAll('tr'):

            cc_tmp, bb_spot, bs_spot, bb_cash, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]
            cc = cc_tmp.split()[0].strip()

            fx_item[cc] = {
                'bb_spot':__format_fx(bb_spot), 'bs_spot':__format_fx(bs_spot),
                'bb_cash':__format_fx(bb_cash), 'bs_cash':__format_fx(bs_cash)
            }

    elif bank_table_dict['bank_id'] == 'BKTWTWTP-004': # 台灣銀行

        # last updated
        time_str = __parse_datetime(time_soup_str)

        # fx table
        fx_item = {}
        for fx_tr in fx_table_soup.findAll('tr'):

            cc_tmp = fx_tr.find('td', {'data-table':'幣別'}).find('div',{'class':'hidden-phone'}).get_text().strip()
            cc = re.search(r'.*\((.+?)\).*', cc_tmp).group(1)

            bb_spot = fx_tr.find('td', {'data-table':'本行即期買入'}).get_text()
            bs_spot = fx_tr.find('td', {'data-table':'本行即期賣出'}).get_text()
            bb_cash = fx_tr.find('td', {'data-table':'本行現金買入'}).get_text()
            bs_cash = fx_tr.find('td', {'data-table':'本行現金賣出'}).get_text()

            fx_item[cc] = {
                'bb_spot':__format_fx(bb_spot), 'bs_spot':__format_fx(bs_spot),
                'bb_cash':__format_fx(bb_cash), 'bs_cash':__format_fx(bs_cash)
            }

    elif bank_table_dict['bank_id'] == 'CCBCTWTP-009':  # 彰銀

        # last updated
        time_str = __parse_datetime(time_soup_str)

        # fx table
        fx_item = defaultdict(lambda:{'bb_cash':'-', 'bs_cash':'-', 'bb_spot':'-', 'bs_spot':'-'})
        for fx_tr in fx_table_soup.findAll('tr'):

            cc_tmp, bb, bs = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]
            cc = re.search(r'.*\((.+?)\).*', cc_tmp).group(1).strip()

            if '-C' in cc_tmp:
                cc = cc[:3]
                fx_item[cc]['bb_cash'], fx_item[cc]['bs_cash'] = __format_fx(bb), __format_fx(bs)
            else:
                fx_item[cc]['bb_spot'], fx_item[cc]['bs_spot'] = __format_fx(bb), __format_fx(bs)
        fx_item = dict(fx_item)

    elif bank_table_dict['bank_id'] == 'CDIBTWTP-809':  # 凱基

        # last updated
        time_str = __parse_datetime(time_soup_str)

        # fx table
        fx_item = {}
        for fx_tr in fx_table_soup.findAll('tr')[2:]:

            cc, _, bb_spot, bs_spot, bb_cash, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td')[:6] ]

            fx_item[cc] = {
                'bb_spot':__format_fx(bb_spot), 'bs_spot':__format_fx(bs_spot),
                'bb_cash':__format_fx(bb_cash), 'bs_cash':__format_fx(bs_cash)
            }

    elif bank_table_dict['bank_id'] == 'COBKTWTP-147':  # 三信

        # last updated
        time_str = __parse_datetime(time_soup_str, year_offset=1911)

        # fx table
        fx_item = {}
        for fx_tr in fx_table_soup.findAll('tr')[2:]:

            cc_tmp, bb_spot, bs_spot, bb_cash, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]
            cc = cc_tmp[-3:]

            fx_item[cc] = {
                'bb_spot':__format_fx(bb_spot), 'bs_spot':__format_fx(bs_spot),
                'bb_cash':__format_fx(bb_cash), 'bs_cash':__format_fx(bs_cash)
            }

    elif bank_table_dict['bank_id'] == 'CTCBTWTP-822':  # 中國信託

        # last updated
        time_str = __parse_datetime(time_soup_str)

        # fx table
        fx_item = {}
        for fx_tr in fx_table_soup.findAll('tr')[1:]:

            cc_tmp, bb_cash, bs_cash, bb_spot, bs_spot = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]
            cc = cc_tmp.split('/')[1].strip()

            fx_item[cc] = {
                'bb_spot':__format_fx(bb_spot), 'bs_spot':__format_fx(bs_spot),
                'bb_cash':__format_fx(bb_cash), 'bs_cash':__format_fx(bs_cash)
            }

    elif bank_table_dict['bank_id'] == 'DBSSTWTP-810': # 星展

        # last updated
        time_str = datetime.strptime(time_soup_str,'%d/%m/%Y %I:%M %p').strftime("%Y-%m-%d %H:%M")

        # fx table
        fx_item = {}
        for fx_tr in fx_table_soup.find('tbody').findAll('tr'):

            cc, bs_spot, bb_spot, bs_cash, bb_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td')[1:] ]

            fx_item[cc] = {
                'bb_spot':__format_fx(bb_spot), 'bs_spot':__format_fx(bs_spot),
                'bb_cash':__format_fx(bb_cash), 'bs_cash':__format_fx(bs_cash)
            }

    elif bank_table_dict['bank_id'] == 'ENTITWTP-816':  # 安泰

        # last updated
        time_str = __parse_datetime(time_soup_str, year_offset=1911)

        # fx table
        fx_item = {}
        for fx_tr in fx_table_soup.findAll('tr')[1:]:

            cc_tmp, bb_spot, bs_spot, bb_cash, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]
            cc = cc_tmp.split()[-1].strip()

            fx_item[cc] = {
                'bb_spot':__format_fx(bb_spot), 'bs_spot':__format_fx(bs_spot),
                'bb_cash':__format_fx(bb_cash), 'bs_cash':__format_fx(bs_cash)
            }

    elif bank_table_dict['bank_id'] == 'ESUNTWTP-808': # 玉山

        # last updated
        time_str = __parse_datetime(time_soup_str)

        # fx table
        fx_item = {}
        for fx_tr in fx_table_soup.findAll('tr', {'class':'tableContent-light'}):

            cc_tmp = fx_tr.find('td', {'class':'itemTtitle'}).find('a').get_text().strip()
            cc = re.search(r'.*\((.+?)\).*', cc_tmp).group(1)

            bb_spot = fx_tr.find('td', {'data-name':'即期買入匯率'}).get_text()
            bs_spot = fx_tr.find('td', {'data-name':'即期賣出匯率'}).get_text()
            bb_cash = fx_tr.find('td', {'data-name':'現金買入匯率'}).get_text()
            bs_cash = fx_tr.find('td', {'data-name':'現金賣出匯率'}).get_text()

            fx_item[cc] = {
                'bb_spot':__format_fx(bb_spot), 'bs_spot':__format_fx(bs_spot),
                'bb_cash':__format_fx(bb_cash), 'bs_cash':__format_fx(bs_cash)
            }

    elif bank_table_dict['bank_id'] == 'FCBKTWTP-007':  # 第一銀

        # last updated
        time_str = __parse_datetime(time_soup_str)

        # fx table
        fx_item = defaultdict(lambda:{'bb_cash':'-', 'bs_cash':'-', 'bb_spot':'-', 'bs_spot':'-'})
        for fx_tr in fx_table_soup.findAll('tr')[1:-1]:

            cc, fx_type, bb, bs = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td')[:4] ]
            if r'(' in cc: cc = re.search(r'.*\((.+?)\).*', cc).group(1).strip()

            if fx_type == 'Cash':
                fx_item[cc]['bb_cash'], fx_item[cc]['bs_cash'] = __format_fx(bb), __format_fx(bs)
            else:
                fx_item[cc]['bb_spot'], fx_item[cc]['bs_spot'] = __format_fx(bb), __format_fx(bs)
        fx_item = dict(fx_item)

    elif bank_table_dict['bank_id'] == 'FEINTWTP-805':  # 遠銀

        # last updated
        time_str = datetime.today().strftime("%Y-%m-%d %H:%M")

        # fx table
        fx_item = {}
        for fx_tr in fx_table_soup.find('div').findAll('div', recursive=False)[1:]:

            cc_tmp, bb_spot, bs_spot, bb_cash, bs_cash = [ fx_td.find('span').find('span').get_text() for fx_td in fx_tr.findAll('div')[:-1] ]
            cc = cc_tmp.split()[1].strip()

            fx_item[cc] = {
                'bb_spot':__format_fx(bb_spot), 'bs_spot':__format_fx(bs_spot),
                'bb_cash':__format_fx(bb_cash), 'bs_cash':__format_fx(bs_cash)
            }

    elif bank_table_dict['bank_id'] == 'HNBKTWTP-008':  # 華南

        # last updated
        time_str = __parse_datetime(time_soup_str)

        # fx table
        fx_item = defaultdict(lambda:{'bb_cash':'-', 'bs_cash':'-', 'bb_spot':'-', 'bs_spot':'-'})
        for fx_tr in fx_table_soup.findAll('tr'):

            cc_tmp, bb, bs = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]
            cc = cc_tmp.split()[0].strip()

            if 'CASH' in cc_tmp:
                fx_item[cc]['bb_cash'], fx_item[cc]['bs_cash'] = __format_fx(bb), __format_fx(bs)
            else:
                fx_item[cc]['bb_spot'], fx_item[cc]['bs_spot'] = __format_fx(bb), __format_fx(bs)
        fx_item = dict(fx_item)

    elif bank_table_dict['bank_id'] == 'HSBCTWTP-081':  # 滙豐

        # last updated
        time_str = __parse_datetime(time_soup_str, parse_time=False)

        # fx table
        fx_item = {}
        for fx_tr in fx_table_soup.findAll('tr')[3:]:

            cc_tmp, bb_spot, bs_spot, bb_cash, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]
            cc = re.search(r'.*\((.+?)\).*', cc_tmp).group(1)

            fx_item[cc] = {
                'bb_spot':__format_fx(bb_spot), 'bs_spot':__format_fx(bs_spot),
                'bb_cash':__format_fx(bb_cash), 'bs_cash':__format_fx(bs_cash)
            }

    elif bank_table_dict['bank_id'] == 'IBOTTWTP-048': # 王道

        # last updated
        time_str = __parse_datetime(time_soup_str)

        # fx table
        fx_tr_list_bs = fx_table_soup.find('div', {'id':'layout_0_main_default_0_lv_fxContent_tabContent_0'}).findAll('li', {'class':'n-table'})
        fx_tr_list_bb = fx_table_soup.find('div', {'id':'layout_0_main_default_0_lv_fxContent_tabContent_1'}).findAll('li', {'class':'n-table'})

        fx_item = {}
        for fx_tr_bs, fx_tr_bb in zip(fx_tr_list_bs, fx_tr_list_bb):

            fx_tr_bs_list = fx_tr_bs.findAll('span', {'class':'w3-col'})
            fx_tr_bb_list = fx_tr_bb.findAll('span', {'class':'w3-col'})

            cc = fx_tr_bs_list[0].findAll('span')[2].get_text().strip()

            fx_item[cc] = {
                'bb_spot':__format_fx(fx_tr_bb_list[1].get_text()), 'bs_spot':__format_fx(fx_tr_bs_list[1].get_text()),
                'bb_cash':__format_fx(fx_tr_bb_list[2].get_text()), 'bs_cash':__format_fx(fx_tr_bs_list[2].get_text())
            }

    elif bank_table_dict['bank_id'] == 'ICBCTWTP-017':  # 兆豐

        # last updated
        time_str = __parse_datetime(time_soup_str)

        # fx table
        fx_item = {}
        for fx_tr in fx_table_soup.findAll('tr'):

            cc_tmp, bb_spot, bb_cash, bs_spot, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td')[:-1] ]
            cc = re.search(r'.*\[(.+?)\].*', cc_tmp).group(1)

            fx_item[cc] = {
                'bb_spot':__format_fx(bb_spot), 'bs_spot':__format_fx(bs_spot),
                'bb_cash':__format_fx(bb_cash), 'bs_cash':__format_fx(bs_cash)
            }

    elif bank_table_dict['bank_id'] == 'JSIBTWTP-815':  # 日盛

        # last updated
        time_str = __parse_datetime(time_soup_str)

        # fx table
        fx_item = {}
        for fx_tr in fx_table_soup.findAll('tr')[1:]:

            cc_tmp, bb_spot, bs_spot, bb_cash, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]
            cc = CURRENCY2ID[cc_tmp]

            fx_item[cc] = {
                'bb_spot':__format_fx(bb_spot), 'bs_spot':__format_fx(bs_spot),
                'bb_cash':__format_fx(bb_cash), 'bs_cash':__format_fx(bs_cash)
            }

    elif bank_table_dict['bank_id'] == 'LBOTTWTP-005': # 土地

        # last updated
        time_str = __parse_datetime(time_soup_str)

        # fx table
        fx_item = {}
        for fx_tr in fx_table_soup.findAll('tr'):

            cc_tmp, bb_spot, bs_spot, bb_cash, bs_cash = fx_tr.findAll('td')[:5]
            cc = re.search(r'.*\((.+?)\).*', cc_tmp.find('label').get_text()).group(1).strip()

            fx_item[cc] = {
                'bb_spot':__format_fx(bb_spot.find('div').get_text()), 'bs_spot':__format_fx(bs_spot.find('div').get_text()),
                'bb_cash':__format_fx(bb_cash.find('div').get_text()), 'bs_cash':__format_fx(bs_cash.find('div').get_text())
            }

    elif bank_table_dict['bank_id'] == 'MBBTTWTP-050':  # 台灣企銀

        # last updated
        time_str = __parse_datetime(time_soup_str)

        # fx table
        fx_item = defaultdict(lambda:{'bb_cash':'-', 'bs_cash':'-', 'bb_spot':'-', 'bs_spot':'-'})
        for fx_tr in fx_table_soup.findAll('tr'):

            fx_type, bb, bs = [ td_bs.get_text().strip() for td_bs in fx_tr.findAll('td') ]
            cc = CURRENCY2ID[ fx_tr.find('th').get_text().strip() ]

            if 'CASH' == fx_type:
                fx_item[cc]['bb_cash'], fx_item[cc]['bs_cash'] = __format_fx(bb), __format_fx(bs)
            elif 'SPOT' == fx_type:
                fx_item[cc]['bb_spot'], fx_item[cc]['bs_spot'] = __format_fx(bb), __format_fx(bs)
        fx_item = dict(fx_item)

    elif bank_table_dict['bank_id'] == 'MKTBTWTP-103':  # 新光

        # last updated
        time_str = __parse_datetime(time_soup_str)

        # fx table
        fx_item = {}
        for fx_tr in fx_table_soup.findAll('ul')[1:]:

            cc, _, bb_spot, bs_spot, bb_cash, bs_cash = [ fx_td.find('p').get_text().strip() for fx_td in fx_tr.findAll('li')[:-1] ]

            fx_item[cc] = {
                'bb_spot':__format_fx(bb_spot), 'bs_spot':__format_fx(bs_spot),
                'bb_cash':__format_fx(bb_cash), 'bs_cash':__format_fx(bs_cash)
            }

    elif bank_table_dict['bank_id'] == 'SCBLTWTP-052':  # 渣打

        # last updated
        time_str = __parse_datetime(time_soup_str)

        # fx table
        fx_item = {}
        for fx_tr in fx_table_soup.findAll('tr')[1:]:

            bb_cash, bs_cash, bb_spot, bs_spot = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]
            cc = fx_tr.find('th').get_text().strip()

            fx_item[cc] = {
                'bb_spot':__format_fx(bb_spot), 'bs_spot':__format_fx(bs_spot),
                'bb_cash':__format_fx(bb_cash), 'bs_cash':__format_fx(bs_cash)
            }

    elif bank_table_dict['bank_id'] == 'SCSBTWTP-011':  # 上海

        # last updated
        time_str = __parse_datetime(time_soup_str, year_offset=1911)

        # fx table
        fx_item = defaultdict(lambda:{'bb_cash':'-', 'bs_cash':'-', 'bb_spot':'-', 'bs_spot':'-'})
        for fx_tr in fx_table_soup.findAll('tr')[3:]:

            cc, bb, bs = [ fx_td.find('span').get_text().strip() for fx_td in fx_tr.findAll('td')[1:] ]

            if 'CASH' in cc:
                cc = cc.split()[0]
                fx_item[cc]['bb_cash'], fx_item[cc]['bs_cash'] = __format_fx(bb), __format_fx(bs)
            else:
                fx_item[cc]['bb_spot'], fx_item[cc]['bs_spot'] = __format_fx(bb), __format_fx(bs)
        fx_item = dict(fx_item)

    elif bank_table_dict['bank_id'] == 'SINOTWTP-700': # 中郵

        # last updated
        time_str = __parse_datetime(time_soup_str, year_offset=1911, parse_time=False)

        # fx table
        fx_item = {}
        for fx_tr in fx_table_soup.find('div', {'id':'css_table1'}).findAll('div', recursive=False)[1:]:

            cc_tmp, bb_spot, bb_cash, bs_spot, bs_cash = [ fx_td.get_text() for fx_td in fx_tr.findAll('div') ]
            cc = re.search(r'.*\((.+?)\).*', cc_tmp).group(1).strip()

            fx_item[cc] = {
                'bb_spot':__format_fx(bb_spot), 'bs_spot':__format_fx(bs_spot),
                'bb_cash':__format_fx(bb_cash), 'bs_cash':__format_fx(bs_cash)
            }

    elif bank_table_dict['bank_id'] == 'SINOTWTP-807':  # 永豐

        # last updated
        time_str = __parse_datetime(time_soup_str)

        # fx table
        fx_item = {}
        for fx_tr in fx_table_soup.findAll('tr')[2:]:

            bb_spot, bs_spot, bb_cash, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td')[1:] ]
            cc = re.search(r'.*\((.+?)\).*', fx_tr.find('td').find('div').get_text().strip()).group(1).strip()

            fx_item[cc] = {
                'bb_spot':__format_fx(bb_spot), 'bs_spot':__format_fx(bs_spot),
                'bb_cash':__format_fx(bb_cash), 'bs_cash':__format_fx(bs_cash)
            }

    elif bank_table_dict['bank_id'] == 'SUNYTWTP-108':  # 陽信

        # last updated
        time_str = __parse_datetime(time_soup_str)

        # fx table
        fx_item = {}
        for fx_tr in fx_table_soup.findAll('tr'):

            bb_cash, bs_cash, bb_spot, bs_spot = [ fx_td.get_text() for fx_td in fx_tr.findAll('td')[1:] ]
            cc = CURRENCY2ID[ fx_tr.find('td').findAll('span')[-1].get_text().strip() ]

            fx_item[cc] = {
                'bb_spot':__format_fx(bb_spot, extract=True), 'bs_spot':__format_fx(bs_spot, extract=True),
                'bb_cash':__format_fx(bb_cash, extract=True), 'bs_cash':__format_fx(bs_cash, extract=True)
            }

    elif bank_table_dict['bank_id'] == 'TACBTWTP-006':  # 合庫

        # last updated
        time_str = __parse_datetime(time_soup_str, year_offset=1911)

        # fx table
        fx_tr_list_bs = fx_table_soup.findAll('tr', {'class':'content-bk-line'})
        fx_tr_list_bb = fx_table_soup.findAll('tr', {'class':'content-line'})

        fx_item = {}
        for fx_tr_bs, fx_tr_bb in zip(fx_tr_list_bs, fx_tr_list_bb):

            cc, _, bs_spot, bs_cash = [ td_bs.find('span').get_text().strip() for td_bs in fx_tr_bs.findAll('td')[:4] ]
            bb_spot, bb_cash = [ td_bb.find('span').get_text().strip() for td_bb in fx_tr_bb.findAll('td')[2:4] ]

            fx_item[cc] = {
                'bb_spot':__format_fx(bb_spot), 'bs_spot':__format_fx(bs_spot),
                'bb_cash':__format_fx(bb_cash), 'bs_cash':__format_fx(bs_cash)
            }

    elif bank_table_dict['bank_id'] == 'TCBBTWTH-053':  # 台中銀行

        # last updated
        time_str = __parse_datetime(time_soup_str)

        # fx table
        fx_item = {}
        for fx_tr in fx_table_soup.findAll('tr')[1:]:

            cc_tmp, bb_cash, bs_cash, bb_spot, bs_spot = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]
            cc = cc_tmp.split()[1].strip()

            fx_item[cc] = {
                'bb_spot':__format_fx(bb_spot), 'bs_spot':__format_fx(bs_spot),
                'bb_cash':__format_fx(bb_cash), 'bs_cash':__format_fx(bs_cash)
            }

    elif bank_table_dict['bank_id'] == 'TNBBTWTN-054':  # 京城

        # last updated
        time_str = __parse_datetime(time_soup_str, year_offset=1911)

        # fx table
        fx_item = {}
        for fx_tr in fx_table_soup.findAll('tr')[2:-2]:

            cc, bb_spot, bs_spot, bb_cash, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td')[1:] ]

            fx_item[cc] = {
                'bb_spot':__format_fx(bb_spot), 'bs_spot':__format_fx(bs_spot),
                'bb_cash':__format_fx(bb_cash), 'bs_cash':__format_fx(bs_cash)
            }

    elif bank_table_dict['bank_id'] == 'TPBKTWTP-012': # 富邦

        # last updated
        time_str = __parse_datetime(time_soup_str)

        # fx table
        fx_item = {}
        for fx_tr in fx_table_soup.findAll('tr'):

            _, cc_tmp, _, spot, cash = fx_tr.findAll('td')

            cc = re.search(r'.*\((.+?)\).*', cc_tmp.find('div').get_text()).group(1).strip()
            spot = spot.find('div').get_text().split()
            cash = cash.find('div').get_text().split()

            if len(spot) == 2:
                bb_spot, bs_spot = spot[0], spot[1]
            else:
                bb_spot, bs_spot = '-', '-'

            if len(cash) == 2:
                bb_cash, bs_cash = cash[0], cash[1]
            else:
                bb_cash, bs_cash = '-', '-'

            fx_item[cc] = {
                'bb_spot':__format_fx(bb_spot), 'bs_spot':__format_fx(bs_spot),
                'bb_cash':__format_fx(bb_cash), 'bs_cash':__format_fx(bs_cash)
            }

    elif bank_table_dict['bank_id'] == 'TSIBTWTP-812':  # 台新

        # last updated
        time_str = __parse_datetime(time_soup_str)

        # fx table
        fx_item = {}
        for fx_tr in fx_table_soup.findAll('tr')[1:]:

            cc_tmp, bb_spot, bs_spot, bb_cash, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]
            cc = cc_tmp.strip()[-3:].strip()

            fx_item[cc] = {
                'bb_spot':__format_fx(bb_spot), 'bs_spot':__format_fx(bs_spot),
                'bb_cash':__format_fx(bb_cash), 'bs_cash':__format_fx(bs_cash)
            }

    elif bank_table_dict['bank_id'] == 'UBOTTWTP-803':  # 聯邦

        # last updated
        time_str = __parse_datetime(time_soup_str, year_offset=1911, re_pattern=r'[^0-9]*(\d+)\/(\d+)\/(\d+)[^0-9]*(\d+):(\d+).*')

        # fx table
        fx_item = {}
        for fx_tr in fx_table_soup.findAll('tr')[2:]:

            cc_tmp, bb_spot, bs_spot, bb_cash, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]
            cc = cc_tmp.split('/')[1].strip()

            fx_item[cc] = {
                'bb_spot':__format_fx(bb_spot), 'bs_spot':__format_fx(bs_spot),
                'bb_cash':__format_fx(bb_cash), 'bs_cash':__format_fx(bs_cash)
            }

    elif bank_table_dict['bank_id'] == 'UWCBTWTP-013': # 國泰

        # last updated
        time_str = __parse_datetime(time_soup_str)

        # fx table
        fx_item = defaultdict(lambda:{'bb_cash':'-', 'bs_cash':'-', 'bb_spot':'-', 'bs_spot':':'})

        for fx_tr in fx_table_soup.findAll('tr'):

            cc_tmp, bb, bs = [ fx_td.find('font').get_text().strip() for fx_td in fx_tr.findAll('td') ]
            cc = re.search('.*\((.+?)\).*', cc_tmp).group(1)

            if 'Cash' in cc_tmp:
                fx_item[cc]['bb_cash'], fx_item[cc]['bs_cash'] = __format_fx(bb), __format_fx(bs)
            else:
                fx_item[cc]['bb_spot'], fx_item[cc]['bs_spot'] = __format_fx(bb), __format_fx(bs)
        fx_item = dict(fx_item)

    elif bank_table_dict['bank_id'] == 'CITITWTX-021':  # 花旗

        # last updated
        time_str = datetime.today().strftime("%Y-%m-%d")

        # fx table
        fx_item = {}
        for fx_tr in fx_table_soup.findAll('tr')[2:]:

            cc, bs_spot, bb_spot, bs_cash, bb_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td')[1:] ]

            fx_item[cc] = {
                'bb_spot':__format_fx(bb_spot), 'bs_spot':__format_fx(bs_spot),
                'bb_cash':__format_fx(bb_cash), 'bs_cash':__format_fx(bs_cash)
            }

    return { 'bank_id':bank_table_dict['bank_id'], 'bank_name':bank_table_dict['cn_name'], 'last_updated':time_str, 'fx_table':fx_item }


def __format_fx(num, extract=False):

    if num:
        num = num.strip()

    if extract:
        match = re.search(r'[^0-9]*(\d+\.\d+)[^0-9]*', num)
        if not (match is None):
            num = match.group(1).strip()

    if re.match("^\d+\.\d+$", num):

        num = "%.5f" % float(num)

        if num != '0.00000': return num
        else: return '-'

    else: return '-'


def __parse_datetime(target, re_pattern=None, parse_time=True, year_offset=0):

    if parse_time:

        if re_pattern:
            regex_pattern = re_pattern
        else:
            regex_pattern = r'[^0-9]*(\d+)[-年\ \/]*(\d+)[-月\ \/]*(\d+)[^0-9]*(\d+)[:：時\ ]*(\d+).*'

        year, month, day, hour, minute = re.search(regex_pattern, target, re.DOTALL).group(1, 2, 3, 4, 5)
        year = int(year)+year_offset
        hour = int(hour)+12 if (('下午' in target) or ('PM' in target)) else int(hour)
        time_str = datetime.strptime("{}-{}-{} {}:{}".format(year, month, day, hour, minute),"%Y-%m-%d %H:%M").strftime("%Y-%m-%d %H:%M")

    else:

        if re_pattern:
            regex_pattern = re_pattern
        else:
            regex_pattern = r'[^0-9]*(\d+)[-年\ \/]*(\d+)[-月\ \/]*(\d+).*'

        year, month, day = re.search(regex_pattern, target, re.DOTALL).group(1, 2, 3)
        year = int(year)+year_offset
        time_str = datetime.strptime("{}-{}-{}".format(year, month, day),"%Y-%m-%d").strftime("%Y-%m-%d")

    return time_str


if __name__ == '__main__':

    args = ParseArgs()

    with open(args.bank_table, 'r') as in_file:
        bank_table = json.load(in_file)

    result_list = StartBankCrawlersMultiprocessing(args=args, bank_table=bank_table, processes=args.processes)

    Output(args, result_list)
