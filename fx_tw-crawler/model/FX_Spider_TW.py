

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

import pymysql


DEBUG_MODE = True


class FX_Spider_TW():

    def __init__(self, currency2id, chrome_driver_path, chrome_options=None, debug=DEBUG_MODE):
        self.currency2id = currency2id
        self.chrome_browser = self.__new_chrome_browser(chrome_driver_path, chrome_options)
        self.mariadb_connection = None
        self.debug = debug

    def __new_chrome_browser(self, chrome_driver_path, chrome_options=None, os_name='linux'):

        if chrome_options is None:

            options = webdriver.ChromeOptions()
            options.add_argument('headless')
            options.add_argument('window-size=1200,900');

            if os_name == 'darwin':
                options.add_argument('user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"')

            elif os_name == 'linux':
                options.add_argument('user-agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Chrome/71.0.3578.98"')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-infobars')
                options.add_argument('--disable-dev-shm-usage');
                options.add_argument('--disable-extensions')

        else:
            options = chrome_options

        return webdriver.Chrome(executable_path=chrome_driver_path, options=options)


    def SeleniumOpenUrl(self, url, click_xpaths=[], delay=1):

        self.chrome_browser.get(url)
        time.sleep(delay)

        for click_xpath in click_xpaths:
            WebDriverWait(self.chrome_browser, 10).until(
                EC.presence_of_element_located((By.XPATH, click_xpath))
                ).click()
            time.sleep(delay)

        page_source = self.chrome_browser.page_source
        self.chrome_browser.close()

        return page_source


    def ParseBankFX(self, page_source, bank_id, last_updated_xpath, fx_table_xpath):

        xml_tree = etree.HTML(page_source)

        if not (last_updated_xpath is None):
            time_soup_str = BeautifulSoup(
                etree.tostring(xml_tree.xpath(last_updated_xpath)[0]), features="lxml").get_text().strip()

        if not (fx_table_xpath is None):
            fx_table_soup = BeautifulSoup( etree.tostring(xml_tree.xpath(fx_table_xpath)[0]), features="lxml" )

        if bank_id == 'APBKTWTH-806': # 元大

            # last updated
            time_str = self.__parse_datetime(time_soup_str, year_offset=1911)

            # fx table
            fx_item = {}
            for fx_tr in fx_table_soup.findAll('tr')[1:]:

                cc_tmp, bb_spot, bs_spot, bb_cash, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td')[:5] ]
                cc = re.search(r'.*\((.+?)\).*', cc_tmp).group(1).strip()

                if self.debug:
                    print (bank_id, cc, bb_spot, bs_spot, bb_cash, bs_cash)

                fx_item[cc] = {
                    'bb_spot':self.__format_fx(bb_spot), 'bs_spot':self.__format_fx(bs_spot),
                    'bb_cash':self.__format_fx(bb_cash), 'bs_cash':self.__format_fx(bs_cash)
                }

        elif bank_id == 'BBBKTWTP-118':  # 板信

            # last updated
            time_str = self.__parse_datetime(time_soup_str, year_offset=1911, re_pattern=r'[^0-9]*(\d+)年[^0-9]*(\d+)[^0-9]*(\d+)日[^0-9]*(\d+):(\d+).*')

            # fx table
            fx_item = {}
            for fx_tr in fx_table_soup.findAll('tr')[1:]:

                cc_tmp, bb_spot, bs_spot, bb_cash, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]
                cc = self.currency2id[cc_tmp]

                if self.debug:
                    print (bank_id, cc, bb_spot, bs_spot, bb_cash, bs_cash)

                fx_item[cc] = {
                    'bb_spot':self.__format_fx(bb_spot), 'bs_spot':self.__format_fx(bs_spot),
                    'bb_cash':self.__format_fx(bb_cash), 'bs_cash':self.__format_fx(bs_cash)
                }

        elif bank_id == 'BKAOTWTK-016':  # 高雄銀行

            # last updated
            time_str = self.__parse_datetime(time_soup_str, parse_time=False)

            # fx table
            fx_item = {}
            for fx_tr in fx_table_soup.findAll('tr'):

                cc_tmp, bb_spot, bs_spot, bb_cash, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]
                cc = cc_tmp.split()[0].strip()

                if self.debug:
                    print (bank_id, cc, bb_spot, bs_spot, bb_cash, bs_cash)

                fx_item[cc] = {
                    'bb_spot':self.__format_fx(bb_spot), 'bs_spot':self.__format_fx(bs_spot),
                    'bb_cash':self.__format_fx(bb_cash), 'bs_cash':self.__format_fx(bs_cash)
                }

        elif bank_id == 'BKTWTWTP-004': # 台灣銀行

            # last updated
            time_str = self.__parse_datetime(time_soup_str)

            # fx table
            fx_item = {}
            for fx_tr in fx_table_soup.findAll('tr'):

                cc_tmp = fx_tr.find('td', {'data-table':'幣別'}).find('div',{'class':'hidden-phone'}).get_text().strip()
                cc = re.search(r'.*\((.+?)\).*', cc_tmp).group(1)

                bb_spot = fx_tr.find('td', {'data-table':'本行即期買入'}).get_text()
                bs_spot = fx_tr.find('td', {'data-table':'本行即期賣出'}).get_text()
                bb_cash = fx_tr.find('td', {'data-table':'本行現金買入'}).get_text()
                bs_cash = fx_tr.find('td', {'data-table':'本行現金賣出'}).get_text()

                if self.debug:
                    print (bank_id, cc_tmp, bb_spot, bs_spot, bb_cash, bs_cash)

                fx_item[cc] = {
                    'bb_spot':self.__format_fx(bb_spot), 'bs_spot':self.__format_fx(bs_spot),
                    'bb_cash':self.__format_fx(bb_cash), 'bs_cash':self.__format_fx(bs_cash)
                }

        elif bank_id == 'CCBCTWTP-009':  # 彰銀

            # last updated
            time_str = self.__parse_datetime(time_soup_str)

            # fx table
            fx_item = defaultdict(lambda:{'bb_cash':'-', 'bs_cash':'-', 'bb_spot':'-', 'bs_spot':'-'})
            for fx_tr in fx_table_soup.findAll('tr'):

                cc_tmp, bb, bs = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]
                cc = re.search(r'.*\((.+?)\).*', cc_tmp).group(1).strip()

                if self.debug:
                    print (bank_id, cc, bb, bs)

                if '-C' in cc_tmp:
                    cc = cc[:3]
                    fx_item[cc]['bb_cash'], fx_item[cc]['bs_cash'] = self.__format_fx(bb), self.__format_fx(bs)
                else:
                    fx_item[cc]['bb_spot'], fx_item[cc]['bs_spot'] = self.__format_fx(bb), self.__format_fx(bs)
            fx_item = dict(fx_item)

        elif bank_id == 'CDIBTWTP-809':  # 凱基

            # last updated
            time_str = self.__parse_datetime(time_soup_str)

            # fx table
            fx_item = {}
            for fx_tr in fx_table_soup.findAll('tr')[2:]:

                cc, _, bb_spot, bs_spot, bb_cash, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td')[:6] ]

                if self.debug:
                    print (bank_id, cc, bb_spot, bs_spot, bb_cash, bs_cash)

                fx_item[cc] = {
                    'bb_spot':self.__format_fx(bb_spot), 'bs_spot':self.__format_fx(bs_spot),
                    'bb_cash':self.__format_fx(bb_cash), 'bs_cash':self.__format_fx(bs_cash)
                }

        elif bank_id == 'COBKTWTP-147':  # 三信

            # last updated
            time_str = self.__parse_datetime(time_soup_str, year_offset=1911)

            # fx table
            fx_item = {}
            for fx_tr in fx_table_soup.findAll('tr')[2:]:

                cc_tmp, bb_spot, bs_spot, bb_cash, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]
                cc = cc_tmp[-3:]

                if self.debug:
                    print (bank_id, cc, bb_spot, bs_spot, bb_cash, bs_cash)

                fx_item[cc] = {
                    'bb_spot':self.__format_fx(bb_spot), 'bs_spot':self.__format_fx(bs_spot),
                    'bb_cash':self.__format_fx(bb_cash), 'bs_cash':self.__format_fx(bs_cash)
                }

        elif bank_id == 'CTCBTWTP-822':  # 中國信託

            # last updated
            time_str = self.__parse_datetime(time_soup_str)

            # fx table
            fx_item = {}
            for fx_tr in fx_table_soup.findAll('tr')[1:]:

                cc_tmp, bb_cash, bs_cash, bb_spot, bs_spot = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]
                cc = cc_tmp.split('/')[1].strip()

                if self.debug:
                    print (bank_id, cc, bb_spot, bs_spot, bb_cash, bs_cash)

                fx_item[cc] = {
                    'bb_spot':self.__format_fx(bb_spot), 'bs_spot':self.__format_fx(bs_spot),
                    'bb_cash':self.__format_fx(bb_cash), 'bs_cash':self.__format_fx(bs_cash)
                }

        elif bank_id == 'DBSSTWTP-810': # 星展

            # last updated
            time_str = datetime.strptime(time_soup_str,'%d/%m/%Y %I:%M %p').strftime("%Y-%m-%d %H:%M")

            # fx table
            fx_item = {}
            for fx_tr in fx_table_soup.find('tbody').findAll('tr'):

                cc, bs_spot, bb_spot, bs_cash, bb_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td')[1:] ]

                if self.debug:
                    print (bank_id, cc, bb_spot, bs_spot, bb_cash, bs_cash)

                fx_item[cc] = {
                    'bb_spot':self.__format_fx(bb_spot), 'bs_spot':self.__format_fx(bs_spot),
                    'bb_cash':self.__format_fx(bb_cash), 'bs_cash':self.__format_fx(bs_cash)
                }

        elif bank_id == 'ENTITWTP-816':  # 安泰

            # last updated
            time_str = self.__parse_datetime(time_soup_str, year_offset=1911)

            # fx table
            fx_item = {}
            for fx_tr in fx_table_soup.findAll('tr')[1:]:

                cc_tmp, bb_spot, bs_spot, bb_cash, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]
                cc = cc_tmp.split()[-1].strip()

                if self.debug:
                    print (bank_id, cc, bb_spot, bs_spot, bb_cash, bs_cash)

                fx_item[cc] = {
                    'bb_spot':self.__format_fx(bb_spot), 'bs_spot':self.__format_fx(bs_spot),
                    'bb_cash':self.__format_fx(bb_cash), 'bs_cash':self.__format_fx(bs_cash)
                }

        elif bank_id == 'ESUNTWTP-808': # 玉山

            # last updated
            time_str = self.__parse_datetime(time_soup_str)

            # fx table
            fx_item = {}
            for fx_tr in fx_table_soup.findAll('tr', {'class':'tableContent-light'}):

                cc_tmp = fx_tr.find('td', {'class':'itemTtitle'}).find('a').get_text().strip()
                cc = re.search(r'.*\((.+?)\).*', cc_tmp).group(1)

                bb_spot = fx_tr.find('td', {'data-name':'即期買入匯率'}).get_text()
                bs_spot = fx_tr.find('td', {'data-name':'即期賣出匯率'}).get_text()
                bb_cash = fx_tr.find('td', {'data-name':'現金買入匯率'}).get_text()
                bs_cash = fx_tr.find('td', {'data-name':'現金賣出匯率'}).get_text()

                if self.debug:
                    print (bank_id, cc, bb_spot, bs_spot, bb_cash, bs_cash)

                fx_item[cc] = {
                    'bb_spot':self.__format_fx(bb_spot), 'bs_spot':self.__format_fx(bs_spot),
                    'bb_cash':self.__format_fx(bb_cash), 'bs_cash':self.__format_fx(bs_cash)
                }

        elif bank_id == 'FCBKTWTP-007':  # 第一銀

            # last updated
            time_str = self.__parse_datetime(time_soup_str)

            # fx table
            fx_item = defaultdict(lambda:{'bb_cash':'-', 'bs_cash':'-', 'bb_spot':'-', 'bs_spot':'-'})
            for fx_tr in fx_table_soup.findAll('tr')[1:-1]:

                cc, fx_type, bb, bs = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td')[:4] ]
                if r'(' in cc: cc = re.search(r'.*\((.+?)\).*', cc).group(1).strip()

                if self.debug:
                    print (bank_id, cc, fx_type, bb, bs)

                if fx_type == 'Cash':
                    fx_item[cc]['bb_cash'], fx_item[cc]['bs_cash'] = self.__format_fx(bb), self.__format_fx(bs)
                else:
                    fx_item[cc]['bb_spot'], fx_item[cc]['bs_spot'] = self.__format_fx(bb), self.__format_fx(bs)
            fx_item = dict(fx_item)

        elif bank_id == 'FEINTWTP-805':  # 遠銀

            # last updated
            time_str = datetime.today().strftime("%Y-%m-%d %H:%M")

            # fx table
            fx_item = {}
            for fx_tr in fx_table_soup.find('div').findAll('div', recursive=False)[1:]:

                cc_tmp, bb_spot, bs_spot, bb_cash, bs_cash = [ fx_td.find('span').find('span').get_text() for fx_td in fx_tr.findAll('div')[:-1] ]
                cc = cc_tmp.split()[1].strip()

                if self.debug:
                    print (bank_id, cc, bb_spot, bs_spot, bb_cash, bs_cash)

                fx_item[cc] = {
                    'bb_spot':self.__format_fx(bb_spot), 'bs_spot':self.__format_fx(bs_spot),
                    'bb_cash':self.__format_fx(bb_cash), 'bs_cash':self.__format_fx(bs_cash)
                }

        elif bank_id == 'HNBKTWTP-008':  # 華南

            # last updated
            time_str = self.__parse_datetime(time_soup_str)

            # fx table
            fx_item = defaultdict(lambda:{'bb_cash':'-', 'bs_cash':'-', 'bb_spot':'-', 'bs_spot':'-'})
            for fx_tr in fx_table_soup.findAll('tr'):

                cc_tmp, bb, bs = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]
                cc = cc_tmp.split()[0].strip()

                if self.debug:
                    print (bank_id, cc, bb, bs)

                if 'CASH' in cc_tmp:
                    fx_item[cc]['bb_cash'], fx_item[cc]['bs_cash'] = self.__format_fx(bb), self.__format_fx(bs)
                else:
                    fx_item[cc]['bb_spot'], fx_item[cc]['bs_spot'] = self.__format_fx(bb), self.__format_fx(bs)
            fx_item = dict(fx_item)

        elif bank_id == 'HSBCTWTP-081':  # 滙豐

            # last updated
            time_str = self.__parse_datetime(time_soup_str, parse_time=False)

            # fx table
            fx_item = {}
            for fx_tr in fx_table_soup.findAll('tr')[3:]:

                cc_tmp, bb_spot, bs_spot, bb_cash, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]
                cc = re.search(r'.*\((.+?)\).*', cc_tmp).group(1)

                if self.debug:
                    print (bank_id, cc, bb_spot, bs_spot, bb_cash, bs_cash)

                fx_item[cc] = {
                    'bb_spot':self.__format_fx(bb_spot), 'bs_spot':self.__format_fx(bs_spot),
                    'bb_cash':self.__format_fx(bb_cash), 'bs_cash':self.__format_fx(bs_cash)
                }

        elif bank_id == 'IBOTTWTP-048': # 王道

            # last updated
            time_str = self.__parse_datetime(time_soup_str)

            # fx table
            fx_tr_list_bs_spot = fx_table_soup.find('div', {'id':'layout_0_main_default_0_lv_fxContent_tabContent_0'}).findAll('li', {'class':'n-table'})
            fx_tr_list_bb_spot = fx_table_soup.find('div', {'id':'layout_0_main_default_0_lv_fxContent_tabContent_1'}).findAll('li', {'class':'n-table'})
            fx_tr_list_bs_cash = fx_table_soup.find('div', {'id':'layout_0_main_default_2_lv_fxContent_tabContent_0'}).findAll('li', {'class':'n-table'})
            fx_tr_list_bb_cash = fx_table_soup.find('div', {'id':'layout_0_main_default_2_lv_fxContent_tabContent_1'}).findAll('li', {'class':'n-table'})

            fx_item = defaultdict(lambda:{'bb_cash':'-', 'bs_cash':'-', 'bb_spot':'-', 'bs_spot':'-'})

            for fx_tr_bs, fx_tr_bb in zip(fx_tr_list_bs_spot, fx_tr_list_bb_spot):

                fx_tr_bs_list = fx_tr_bs.find_all(class_='w3-col')
                fx_tr_bb_list = fx_tr_bb.find_all(class_='w3-col')

                cc = fx_tr_bs_list[0].findAll('div')[2].get_text().strip()
                bs_spot = fx_tr_bs_list[2].find('span').get_text().strip()
                bb_spot = fx_tr_bb_list[2].find('span').get_text().strip()

                if self.debug:
                    print (bank_id, cc, bb_spot, bs_spot)

                fx_item[cc]['bb_spot'], fx_item[cc]['bs_spot'] = self.__format_fx(bb_spot), self.__format_fx(bs_spot)

            for fx_tr_bs, fx_tr_bb in zip(fx_tr_list_bs_cash, fx_tr_list_bb_cash):

                fx_tr_bs_list = fx_tr_bs.find('div', {'class':'table-row'}).findAll('span', {'class':'w3-col'})
                fx_tr_bb_list = fx_tr_bb.find('div', {'class':'table-row'}).findAll('span', {'class':'w3-col'})

                cc = fx_tr_bs_list[0].findAll('span')[2].get_text().strip()
                bs_cash = fx_tr_bs_list[1].get_text().strip()
                bb_cash = fx_tr_bb_list[1].get_text().strip()

                if self.debug:
                    print (bank_id, cc, bb_cash, bs_cash)

                fx_item[cc]['bb_cash'], fx_item[cc]['bs_cash'] = self.__format_fx(bb_cash), self.__format_fx(bs_cash)
            fx_item = dict(fx_item)

        elif bank_id == 'ICBCTWTP-017':  # 兆豐

            # last updated
            time_str = self.__parse_datetime(time_soup_str)

            # fx table
            fx_item = {}
            for fx_tr in fx_table_soup.findAll('tr'):

                cc_tmp, bb_spot, bb_cash, bs_spot, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td')[:-1] ]
                cc = re.search(r'.*\[(.+?)\].*', cc_tmp).group(1)

                if self.debug:
                    print (bank_id, cc, bb_spot, bs_spot, bb_cash, bs_cash)

                fx_item[cc] = {
                    'bb_spot':self.__format_fx(bb_spot), 'bs_spot':self.__format_fx(bs_spot),
                    'bb_cash':self.__format_fx(bb_cash), 'bs_cash':self.__format_fx(bs_cash)
                }

        elif bank_id == 'JSIBTWTP-815':  # 日盛

            # last updated
            time_str = self.__parse_datetime(time_soup_str)

            # fx table
            fx_item = {}
            for fx_tr in fx_table_soup.findAll('tr')[1:]:

                cc_tmp, bb_spot, bs_spot, bb_cash, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]
                cc = self.currency2id[cc_tmp]

                if self.debug:
                    print (bank_id, cc, bb_spot, bs_spot, bb_cash, bs_cash)

                fx_item[cc] = {
                    'bb_spot':self.__format_fx(bb_spot), 'bs_spot':self.__format_fx(bs_spot),
                    'bb_cash':self.__format_fx(bb_cash), 'bs_cash':self.__format_fx(bs_cash)
                }

        elif bank_id == 'LBOTTWTP-005': # 土地

            # last updated
            time_str = self.__parse_datetime(time_soup_str)

            # fx table
            fx_item = {}
            for fx_tr in fx_table_soup.findAll('tr'):

                cc_tmp, bb_spot, bs_spot, bb_cash, bs_cash = fx_tr.findAll('td')[:5]
                cc = re.search(r'.*\((.+?)\).*', cc_tmp.find('label').get_text()).group(1).strip()

                if self.debug:
                    print (bank_id, cc, bb_spot.find('div').get_text(), bs_spot.find('div').get_text(), bb_cash.find('div').get_text(), bs_cash.find('div').get_text())

                fx_item[cc] = {
                    'bb_spot':self.__format_fx(bb_spot.find('div').get_text()), 'bs_spot':self.__format_fx(bs_spot.find('div').get_text()),
                    'bb_cash':self.__format_fx(bb_cash.find('div').get_text()), 'bs_cash':self.__format_fx(bs_cash.find('div').get_text())
                }

        elif bank_id == 'MBBTTWTP-050':  # 台灣企銀

            # last updated
            time_str = self.__parse_datetime(time_soup_str)

            # fx table
            fx_item = defaultdict(lambda:{'bb_cash':'-', 'bs_cash':'-', 'bb_spot':'-', 'bs_spot':'-'})
            for fx_tr in fx_table_soup.findAll('tr'):

                fx_type, bb, bs = [ td_bs.get_text().strip() for td_bs in fx_tr.findAll('td') ]
                cc = self.currency2id[ fx_tr.find('th').get_text().strip() ]

                if self.debug:
                    print (bank_id, cc, fx_type, bb, bs)

                if 'CASH' == fx_type:
                    fx_item[cc]['bb_cash'], fx_item[cc]['bs_cash'] = self.__format_fx(bb), self.__format_fx(bs)
                elif 'SPOT' == fx_type:
                    fx_item[cc]['bb_spot'], fx_item[cc]['bs_spot'] = self.__format_fx(bb), self.__format_fx(bs)
            fx_item = dict(fx_item)

        elif bank_id == 'MKTBTWTP-103':  # 新光

            # last updated
            time_str = self.__parse_datetime(time_soup_str)

            # fx table
            fx_item = {}
            for fx_tr in fx_table_soup.findAll('ul')[1:]:

                cc, _, bb_spot, bs_spot, bb_cash, bs_cash = [ fx_td.find('p').get_text().strip() for fx_td in fx_tr.findAll('li')[:-1] ]

                if self.debug:
                    print (bank_id, cc, bb_spot, bs_spot, bb_cash, bs_cash)

                fx_item[cc] = {
                    'bb_spot':self.__format_fx(bb_spot), 'bs_spot':self.__format_fx(bs_spot),
                    'bb_cash':self.__format_fx(bb_cash), 'bs_cash':self.__format_fx(bs_cash)
                }

        elif bank_id == 'SCBLTWTP-052':  # 渣打

            # last updated
            time_str = self.__parse_datetime(time_soup_str)

            # fx table
            fx_item = {}
            for fx_tr in fx_table_soup.findAll('tr')[1:]:

                bb_cash, bs_cash, bb_spot, bs_spot = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]
                cc = fx_tr.find('th').get_text().strip()

                if self.debug:
                    print (bank_id, cc, bb_spot, bs_spot, bb_cash, bs_cash)

                fx_item[cc] = {
                    'bb_spot':self.__format_fx(bb_spot), 'bs_spot':self.__format_fx(bs_spot),
                    'bb_cash':self.__format_fx(bb_cash), 'bs_cash':self.__format_fx(bs_cash)
                }

        elif bank_id == 'SCSBTWTP-011':  # 上海

            # last updated
            time_str = self.__parse_datetime(time_soup_str, year_offset=1911)

            # fx table
            fx_item = defaultdict(lambda:{'bb_cash':'-', 'bs_cash':'-', 'bb_spot':'-', 'bs_spot':'-'})
            for fx_tr in fx_table_soup.findAll('tr')[3:]:

                cc, bb, bs = [ fx_td.find('span').get_text().strip() for fx_td in fx_tr.findAll('td')[1:] ]

                if self.debug:
                    print (bank_id, cc, bb, bs)

                if 'CASH' in cc:
                    cc = cc.split()[0]
                    fx_item[cc]['bb_cash'], fx_item[cc]['bs_cash'] = self.__format_fx(bb), self.__format_fx(bs)
                else:
                    fx_item[cc]['bb_spot'], fx_item[cc]['bs_spot'] = self.__format_fx(bb), self.__format_fx(bs)
            fx_item = dict(fx_item)

        elif bank_id == 'SINOTWTP-700': # 中郵

            # last updated
            time_str = self.__parse_datetime(time_soup_str, year_offset=1911, parse_time=False)

            # fx table
            fx_item = {}
            for fx_tr in fx_table_soup.find('div', {'id':'css_table1'}).findAll('div', recursive=False)[1:]:

                cc_tmp, bb_spot, bb_cash, bs_spot, bs_cash = [ fx_td.get_text() for fx_td in fx_tr.findAll('div') ]
                cc = re.search(r'.*\((.+?)\).*', cc_tmp).group(1).strip()

                if self.debug:
                    print (bank_id, cc, bb_spot, bs_spot, bb_cash, bs_cash)

                fx_item[cc] = {
                    'bb_spot':self.__format_fx(bb_spot), 'bs_spot':self.__format_fx(bs_spot),
                    'bb_cash':self.__format_fx(bb_cash), 'bs_cash':self.__format_fx(bs_cash)
                }

        elif bank_id == 'SINOTWTP-807':  # 永豐

            # last updated
            time_str = self.__parse_datetime(time_soup_str)

            # fx table
            fx_item = {}
            for fx_tr in fx_table_soup.findAll('tr')[2:]:

                bb_spot, bs_spot, bb_cash, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td')[1:] ]
                cc = re.search(r'.*\((.+?)\).*', fx_tr.find('td').find('div').get_text().strip()).group(1).strip()

                if self.debug:
                    print (bank_id, cc, bb_spot, bs_spot, bb_cash, bs_cash)

                fx_item[cc] = {
                    'bb_spot':self.__format_fx(bb_spot), 'bs_spot':self.__format_fx(bs_spot),
                    'bb_cash':self.__format_fx(bb_cash), 'bs_cash':self.__format_fx(bs_cash)
                }

        elif bank_id == 'SUNYTWTP-108':  # 陽信

            # last updated
            time_str = self.__parse_datetime(time_soup_str)

            # fx table
            fx_item = {}
            for fx_tr in fx_table_soup.findAll('tr'):

                bb_cash, bs_cash, bb_spot, bs_spot = [ fx_td.get_text() for fx_td in fx_tr.findAll('td')[1:] ]
                cc = self.currency2id[ fx_tr.find('td').findAll('span')[-1].get_text().strip() ]

                if self.debug:
                    print (bank_id, cc, bb_spot, bs_spot, bb_cash, bs_cash)

                fx_item[cc] = {
                    'bb_spot':self.__format_fx(bb_spot, extract=True), 'bs_spot':self.__format_fx(bs_spot, extract=True),
                    'bb_cash':self.__format_fx(bb_cash, extract=True), 'bs_cash':self.__format_fx(bs_cash, extract=True)
                }

        elif bank_id == 'TACBTWTP-006':  # 合庫

            # last updated
            time_str = self.__parse_datetime(time_soup_str, year_offset=1911)

            # fx table
            fx_tr_list_bs = fx_table_soup.findAll('tr', {'class':'content-bk-line'})
            fx_tr_list_bb = fx_table_soup.findAll('tr', {'class':'content-line'})

            fx_item = {}
            for fx_tr_bs, fx_tr_bb in zip(fx_tr_list_bs, fx_tr_list_bb):

                cc, _, bs_spot, bs_cash = [ td_bs.find('span').get_text().strip() for td_bs in fx_tr_bs.findAll('td')[:4] ]
                bb_spot, bb_cash = [ td_bb.find('span').get_text().strip() for td_bb in fx_tr_bb.findAll('td')[2:4] ]

                if self.debug:
                    print (bank_id, cc, bb_spot, bs_spot, bb_cash, bs_cash)

                fx_item[cc] = {
                    'bb_spot':self.__format_fx(bb_spot), 'bs_spot':self.__format_fx(bs_spot),
                    'bb_cash':self.__format_fx(bb_cash), 'bs_cash':self.__format_fx(bs_cash)
                }

        elif bank_id == 'TCBBTWTH-053':  # 台中銀行

            # last updated
            time_str = self.__parse_datetime(time_soup_str)

            # fx table
            fx_item = {}
            for fx_tr in fx_table_soup.findAll('tr')[1:]:

                cc_tmp, bb_cash, bs_cash, bb_spot, bs_spot = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]
                cc = cc_tmp.split()[1].strip()

                if self.debug:
                    print (bank_id, cc, bb_spot, bs_spot, bb_cash, bs_cash)

                fx_item[cc] = {
                    'bb_spot':self.__format_fx(bb_spot), 'bs_spot':self.__format_fx(bs_spot),
                    'bb_cash':self.__format_fx(bb_cash), 'bs_cash':self.__format_fx(bs_cash)
                }

        elif bank_id == 'TNBBTWTN-054':  # 京城

            # last updated
            time_str = self.__parse_datetime(time_soup_str, year_offset=1911)

            # fx table
            fx_item = {}
            for fx_tr in fx_table_soup.findAll('tr')[2:-2]:

                cc, bb_spot, bs_spot, bb_cash, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td')[1:] ]

                if self.debug:
                    print (bank_id, cc, bb_spot, bs_spot, bb_cash, bs_cash)

                fx_item[cc] = {
                    'bb_spot':self.__format_fx(bb_spot), 'bs_spot':self.__format_fx(bs_spot),
                    'bb_cash':self.__format_fx(bb_cash), 'bs_cash':self.__format_fx(bs_cash)
                }

        elif bank_id == 'TPBKTWTP-012': # 富邦

            # last updated
            time_str = self.__parse_datetime(time_soup_str)

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

                if self.debug:
                    print (bank_id, cc, bb_spot, bs_spot, bb_cash, bs_cash)

                fx_item[cc] = {
                    'bb_spot':self.__format_fx(bb_spot), 'bs_spot':self.__format_fx(bs_spot),
                    'bb_cash':self.__format_fx(bb_cash), 'bs_cash':self.__format_fx(bs_cash)
                }

        elif bank_id == 'TSIBTWTP-812':  # 台新

            # last updated
            time_str = self.__parse_datetime(time_soup_str)

            # fx table
            fx_item = {}
            for fx_tr in fx_table_soup.findAll('tr')[1:]:

                cc_tmp, bb_spot, bs_spot, bb_cash, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]
                cc = cc_tmp.strip()[-3:].strip()

                if self.debug:
                    print (bank_id, cc, bb_spot, bs_spot, bb_cash, bs_cash)

                fx_item[cc] = {
                    'bb_spot':self.__format_fx(bb_spot), 'bs_spot':self.__format_fx(bs_spot),
                    'bb_cash':self.__format_fx(bb_cash), 'bs_cash':self.__format_fx(bs_cash)
                }

        elif bank_id == 'UBOTTWTP-803':  # 聯邦

            # last updated
            time_str = self.__parse_datetime(time_soup_str, year_offset=1911, re_pattern=r'[^0-9]*(\d+)\/(\d+)\/(\d+)[^0-9]*(\d+):(\d+).*')

            # fx table
            fx_item = {}
            for fx_tr in fx_table_soup.findAll('tr')[2:]:

                cc_tmp, bb_spot, bs_spot, bb_cash, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]
                cc = cc_tmp.split('/')[1].strip()

                if self.debug:
                    print (bank_id, cc, bb_spot, bs_spot, bb_cash, bs_cash)

                fx_item[cc] = {
                    'bb_spot':self.__format_fx(bb_spot), 'bs_spot':self.__format_fx(bs_spot),
                    'bb_cash':self.__format_fx(bb_cash), 'bs_cash':self.__format_fx(bs_cash)
                }

        elif bank_id == 'UWCBTWTP-013': # 國泰

            # last updated
            time_str = self.__parse_datetime(time_soup_str)

            # fx table
            fx_item = defaultdict(lambda:{'bb_cash':'-', 'bs_cash':'-', 'bb_spot':'-', 'bs_spot':':'})

            for fx_tr in fx_table_soup.findAll('tr'):

                cc_tmp, bb, bs = [ fx_td.find('font').get_text().strip() for fx_td in fx_tr.findAll('td') ]
                cc = re.search('.*\((.+?)\).*', cc_tmp).group(1)

                if self.debug:
                    print (bank_id, cc, bb, bs)

                if 'Cash' in cc_tmp:
                    fx_item[cc]['bb_cash'], fx_item[cc]['bs_cash'] = self.__format_fx(bb), self.__format_fx(bs)
                else:
                    fx_item[cc]['bb_spot'], fx_item[cc]['bs_spot'] = self.__format_fx(bb), self.__format_fx(bs)
            fx_item = dict(fx_item)

        elif bank_id == 'CITITWTX-021':  # 花旗

            # last updated
            time_str = datetime.today().strftime("%Y-%m-%d %H:%M")

            # fx table
            fx_item = {}
            for fx_tr in fx_table_soup.findAll('tr')[2:]:

                cc, bs_spot, bb_spot, bs_cash, bb_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td')[1:] ]

                if self.debug:
                    print (bank_id, cc, bb_spot, bs_spot, bb_cash, bs_cash)

                fx_item[cc] = {
                    'bb_spot':self.__format_fx(bb_spot), 'bs_spot':self.__format_fx(bs_spot),
                    'bb_cash':self.__format_fx(bb_cash), 'bs_cash':self.__format_fx(bs_cash)
                }

        return { 'bank_id':bank_id, 'last_updated':time_str, 'fx_table':fx_item }


    def __format_fx(self, num, extract=False):

        if num:
            num = num.strip()

        if extract:
            match = re.search(r'[^0-9]*([0-9\.]+)[^0-9]*', num)
            if not (match is None):
                num = match.group(1).strip()

        if re.match("^[0-9\.]+$", num):

            num = "%.5f" % float(num)

            if num != '0.00000': return num
            else: return '-'

        else: return '-'


    def __parse_datetime(self, target, re_pattern=None, parse_time=True, year_offset=0):

        if parse_time:

            if re_pattern:
                regex_pattern = re_pattern
            else:
                regex_pattern = r'[^0-9]*(\d+)[-年\ \/]*(\d+)[-月\ \/]*(\d+)[^0-9]*(\d+)[:：時\ ]*(\d+).*'

            year, month, day, hour, minute = re.search(regex_pattern, target, re.DOTALL).group(1, 2, 3, 4, 5)
            year = int(year)+year_offset
            hour = int(hour)+12 if ((('下午' in target) or ('PM' in target)) and (int(hour) < 12)) else int(hour)
        else:

            if re_pattern:
                regex_pattern = re_pattern
            else:
                regex_pattern = r'[^0-9]*(\d+)[-年\ \/]*(\d+)[-月\ \/]*(\d+).*'

            year, month, day = re.search(regex_pattern, target, re.DOTALL).group(1, 2, 3)
            year = int(year)+year_offset
            hour, minute = datetime.today().hour, datetime.today().minute

        time_str = datetime.strptime("{}-{}-{} {}:{}".format(year, month, day, hour, minute), "%Y-%m-%d %H:%M").strftime("%Y-%m-%d %H:%M")
        return time_str


    def __connect_mariadb(self, mariadb_config):

        if not mariadb_config: raise

        self.mariadb_connection = (pymysql.connect(
            host=mariadb_config["mariadb_host"],
            port=mariadb_config["mariadb_port"],
            user=mariadb_config["mariadb_user"],
            password=mariadb_config["mariadb_password"],
            database=mariadb_config["mariadb_database"],
            charset=mariadb_config["mariadb_charset"]
        ))

        if not self.mariadb_connection: raise


    def MariaDBSave(self, mariadb_config_path, parsed_fx_dict):

        if (not mariadb_config_path) or (not parsed_fx_dict):
            return None
        else:
            with open(mariadb_config_path, 'r') as in_json:
                mariadb_config = json.load(in_json)
            self.__connect_mariadb(mariadb_config)

        # parsed_fx_dict
        bank_id = parsed_fx_dict['bank_id']
        last_updated = parsed_fx_dict['last_updated']
        fx_item_dict = parsed_fx_dict['fx_table']

        # generate mysql code
        mysql_prefix = "INSERT IGNORE INTO `{}` SET {} = '{}', ".format(bank_id, 'time', last_updated)
        mysql_postfix = ";"

        mysql_list = []
        for fx in fx_item_dict:
            if fx_item_dict[fx]['bb_spot'] != '-':
                mysql_list.append("{}_SPOT_BB = {}".format(fx, fx_item_dict[fx]['bb_spot']))
            if fx_item_dict[fx]['bs_spot'] != '-':
                mysql_list.append("{}_SPOT_BS = {}".format(fx, fx_item_dict[fx]['bs_spot']))
            if fx_item_dict[fx]['bb_cash'] != '-':
                mysql_list.append("{}_CASH_BB = {}".format(fx, fx_item_dict[fx]['bb_cash']))
            if fx_item_dict[fx]['bs_cash'] != '-':
                mysql_list.append("{}_CASH_BS = {}".format(fx, fx_item_dict[fx]['bs_cash']))
        mysql_code = mysql_prefix + ', '.join(mysql_list) + mysql_postfix

        if self.debug:
            print (mysql_code)

        # execute mysql code
        cursor = self.mariadb_connection.cursor()
        cursor.execute(mysql_code)
        self.mariadb_connection.commit()
        cursor.close()


    def Close(self):

        if self.chrome_browser:
            self.chrome_browser.quit()
        if self.mariadb_connection:
            self.mariadb_connection.close()
