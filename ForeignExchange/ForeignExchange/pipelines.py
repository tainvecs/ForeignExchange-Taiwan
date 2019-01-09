# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


from datetime import datetime
from bs4 import BeautifulSoup
import re
from collections import defaultdict
from lxml import etree


class ForeignexchangePipeline(object):


    currency2id = {
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


    def format_fx(self, num):

        if num:
            num = num.strip()

        if re.match("^\d+\.\d+$", num):

            num = "%.5f" % float(num)

            if num != '0.00000': return num
            else: return '-'

        else: return '-'


    def process_item(self, fx_item, spider):

        if fx_item['bank'] == 'BKTWTWTP-004': # 台灣銀行

            # last updated
            fx_item['last_updated'] = datetime.strptime(fx_item['last_updated'].strip(), '%Y/%m/%d %H:%M') \
                .strftime("%Y-%m-%d %H:%M")

            # currency table
            fx_tr_list = BeautifulSoup(fx_item['currency_dict'], features="lxml").findAll('tr')
            fx_item['currency_dict'] = {}

            for fx_tr in fx_tr_list:

                # Currrency Code(CC), Telegraphic Transfer(TT), Bank Buy(BB), Bank Sell(BS)

                cc_tmp = fx_tr.find('td', {'data-table':'幣別'}).find('div',{'class':'hidden-phone'}).get_text().strip()
                cc = re.search('.*\((.+?)\).*', cc_tmp).group(1)

                bb_tt = fx_tr.find('td', {'data-table':'本行即期買入'}).get_text()
                bs_tt = fx_tr.find('td', {'data-table':'本行即期賣出'}).get_text()
                bb_cash = fx_tr.find('td', {'data-table':'本行現金買入'}).get_text()
                bs_cash = fx_tr.find('td', {'data-table':'本行現金賣出'}).get_text()

                fx_item['currency_dict'][cc] = {
                    'bb_tt':self.format_fx(bb_tt), 'bs_tt':self.format_fx(bs_tt),
                    'bb_cash':self.format_fx(bb_cash), 'bs_cash':self.format_fx(bs_cash)
                }


        elif fx_item['bank'] == 'ESUNTWTP-808': # 玉山

            # last updated
            fx_item['last_updated'] = datetime.strptime(fx_item['last_updated'].strip(), '%Y年%m月%d日 %H:%M:%S') \
                .strftime("%Y-%m-%d %H:%M")

            # currency table
            fx_tr_list = BeautifulSoup(fx_item['currency_dict'], features="lxml") \
                .findAll('tr', {'class':'tableContent-light'})
            fx_item['currency_dict'] = {}

            for fx_tr in fx_tr_list:

                # Currrency Code(CC), Telegraphic Transfer(TT), Bank Buy(BB), Bank Sell(BS)

                cc_tmp = fx_tr.find('td', {'class':'itemTtitle'}).find('a').get_text().strip()
                cc = re.search('.*\((.+?)\).*', cc_tmp).group(1)

                bb_tt = fx_tr.find('td', {'data-name':'即期買入匯率'}).get_text()
                bs_tt = fx_tr.find('td', {'data-name':'即期賣出匯率'}).get_text()
                bb_cash = fx_tr.find('td', {'data-name':'現金買入匯率'}).get_text()
                bs_cash = fx_tr.find('td', {'data-name':'現金賣出匯率'}).get_text()

                fx_item['currency_dict'][cc] = {
                    'bb_tt':self.format_fx(bb_tt), 'bs_tt':self.format_fx(bs_tt),
                    'bb_cash':self.format_fx(bb_cash), 'bs_cash':self.format_fx(bs_cash)
                }


        elif fx_item['bank'] == 'IBOTTWTP-048': # 王道

            # last updated
            fx_item['last_updated'] = datetime.strptime(fx_item['last_updated'].strip(),'資料時間：%Y年%m月%d日 %H:%M') \
                .strftime("%Y-%m-%d %H:%M")

            # currency table
            bs_table = BeautifulSoup(fx_item['currency_dict'], features="lxml")
            fx_tr_list_bs = bs_table.find('div', {'id':'layout_0_main_default_0_lv_fxContent_tabContent_0'}) \
                .findAll('li', {'class':'n-table'})
            fx_tr_list_bb = bs_table.find('div', {'id':'layout_0_main_default_0_lv_fxContent_tabContent_1'}) \
                .findAll('li', {'class':'n-table'})
            fx_item['currency_dict'] = {}

            for fx_tr_bs, fx_tr_bb in zip(fx_tr_list_bs, fx_tr_list_bb):

                # Currrency Code(CC), Telegraphic Transfer(TT), Bank Buy(BB), Bank Sell(BS)

                fx_tr_bs_list = fx_tr_bs.findAll('span', {'class':'w3-col'})
                fx_tr_bb_list = fx_tr_bb.findAll('span', {'class':'w3-col'})

                cc = fx_tr_bs_list[0].findAll('span')[2].get_text().strip()

                fx_item['currency_dict'][cc] = {
                    'bb_tt':self.format_fx(fx_tr_bb_list[1].get_text()), 'bs_tt':self.format_fx(fx_tr_bs_list[1].get_text()),
                    'bb_cash':self.format_fx(fx_tr_bb_list[2].get_text()), 'bs_cash':self.format_fx(fx_tr_bs_list[2].get_text())
                }


        elif fx_item['bank'] == 'DBSSTWTP-810': # 星展

            # last updated
            fx_item['last_updated'] = datetime.strptime(fx_item['last_updated'].strip(), '%d/%m/%Y %I:%M %p') \
                .strftime("%Y-%m-%d %H:%M")

            # currency table
            fx_tr_list = BeautifulSoup(fx_item['currency_dict'], features="lxml").find('tbody').findAll('tr')
            fx_item['currency_dict'] = {}

            for fx_tr in fx_tr_list:

                # Currrency Code(CC), Telegraphic Transfer(TT), Bank Buy(BB), Bank Sell(BS)

                cc, bs_tt, bb_tt, bs_cash, bb_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td')[1:] ]

                fx_item['currency_dict'][cc] = {
                    'bb_tt':self.format_fx(bb_tt), 'bs_tt':self.format_fx(bs_tt),
                    'bb_cash':self.format_fx(bb_cash), 'bs_cash':self.format_fx(bs_cash)
                }


        elif fx_item['bank'] == 'APBKTWTH-806': # 元大

            # last updated
            bs_time_1, bs_time_2 = BeautifulSoup(fx_item['last_updated'], features="lxml").findAll('li')
            year, month, day = bs_time_1.find('span').get_text().split('/')
            hour, minute, _ = bs_time_2.find('span').get_text().split(':')
            fx_item['last_updated'] = "{}-{}-{} {}:{}".format(int(year)+1911, month, day, hour, minute)

            # currency table
            fx_tr_list = BeautifulSoup(fx_item['currency_dict'], features="lxml").findAll('tr')[1:]
            fx_item['currency_dict'] = {}

            for fx_tr in fx_tr_list:

                # Currrency Code(CC), Telegraphic Transfer(TT), Bank Buy(BB), Bank Sell(BS)

                cc_tmp, bb_tt, bs_tt, bb_cash, bs_cash = fx_tr.findAll('td')[:5]
                cc = re.search('.*\((.+?)\).*', cc_tmp.find('a').get_text()).group(1).strip()

                fx_item['currency_dict'][cc] = {
                    'bb_tt':self.format_fx(bb_tt.get_text()), 'bs_tt':self.format_fx(bs_tt.get_text()),
                    'bb_cash':self.format_fx(bb_cash.get_text()), 'bs_cash':self.format_fx(bs_cash.get_text())
                }


        elif fx_item['bank'] == 'TPBKTWTP-012': # 富邦

            # last updated
            fx_item['last_updated'] = datetime.strptime(fx_item['last_updated'].strip(), '%Y/%m/%d %H:%M:%S') \
                .strftime("%Y-%m-%d %H:%M")

            # currency table
            fx_tr_list = BeautifulSoup(fx_item['currency_dict'], features="lxml").findAll('tr')
            fx_item['currency_dict'] = {}

            for fx_tr in fx_tr_list:

                # Currrency Code(CC), Telegraphic Transfer(TT), Bank Buy(BB), Bank Sell(BS)

                _, cc_tmp, _, tt, cash = fx_tr.findAll('td')

                cc = re.search('.*\((.+?)\).*', cc_tmp.find('div').get_text()).group(1).strip()
                tt = tt.find('div').get_text().split()
                cash = cash.find('div').get_text().split()

                if len(tt) == 2:
                    bb_tt, bs_tt = self.format_fx(tt[0]), self.format_fx(tt[1])
                else:
                    bb_tt, bs_tt = '-', '-'

                if len(cash) == 2:
                    bb_cash, bs_cash = self.format_fx(cash[0]), self.format_fx(cash[1])
                else:
                    bb_cash, bs_cash = '-', '-'

                fx_item['currency_dict'][cc] = {
                    'bb_tt':bb_tt, 'bs_tt':bs_tt, 'bb_cash':bb_cash, 'bs_cash':bs_cash
                }


        elif fx_item['bank'] == 'UWCBTWTP-013': # 國泰

            # last updated
            fx_item['last_updated'] = datetime.strptime(fx_item['last_updated'].split('：')[1].strip(), '%Y年%m月%d日%H時%M分') \
                .strftime("%Y-%m-%d %H:%M")

            # currency table
            fx_tr_list = BeautifulSoup(fx_item['currency_dict'], features="lxml").findAll('tr')
            fx_item['currency_dict'] = defaultdict(lambda:{'bb_cash':'-', 'bs_cash':'-', 'bb_tt':'-', 'bs_tt':':'})

            for fx_tr in fx_tr_list:

                # Currrency Code(CC), Telegraphic Transfer(TT), Bank Buy(BB), Bank Sell(BS)

                cc_tmp, bb, bs = [ fx_td.find('font').get_text().strip() for fx_td in fx_tr.findAll('td') ]
                cc = re.search('.*\((.+?)\).*', cc_tmp).group(1)

                if 'Cash' in cc_tmp:
                    fx_item['currency_dict'][cc]['bb_cash'] = self.format_fx(bb)
                    fx_item['currency_dict'][cc]['bs_cash'] = self.format_fx(bs)
                else:
                    fx_item['currency_dict'][cc]['bb_tt'] = self.format_fx(bb)
                    fx_item['currency_dict'][cc]['bs_tt'] = self.format_fx(bs)


        elif fx_item['bank'] == 'TACBTWTP-006':  # 合庫

            # last updated
            data_date, data_time = fx_item['last_updated'].split('：')[1:]
            year, month, day = data_date.split()[0].split('/')
            hour, minute, _ = data_time.split(':')
            fx_item['last_updated'] = '{}-{}-{} {}:{}'.format(int(year)+1911, month, day, hour, minute)

            # currency table
            fx_bs = BeautifulSoup(fx_item['currency_dict'], features="lxml")
            fx_tr_list_1 = fx_bs.findAll('tr', {'class':'content-line'})
            fx_tr_list_2 = fx_bs.findAll('tr', {'class':'content-bk-line'})

            fx_item['currency_dict'] = {}

            for fx_tr1, fx_tr2 in zip(fx_tr_list_1, fx_tr_list_2):

                # Currrency Code(CC), Telegraphic Transfer(TT), Bank Buy(BB), Bank Sell(BS)

                bb_tt, bb_cash = [ td_bs.find('span').get_text().strip() for td_bs in fx_tr1.findAll('td')[2:4] ]
                cc, _, bs_tt, bs_cash = [ td_bs.find('span').get_text().strip() for td_bs in fx_tr2.findAll('td')[:4] ]

                fx_item['currency_dict'][cc] = {
                    'bb_tt':self.format_fx(bb_tt), 'bs_tt':self.format_fx(bs_tt),
                    'bb_cash':self.format_fx(bb_cash), 'bs_cash':self.format_fx(bs_cash)
                }


        elif fx_item['bank'] == 'BKAOTWTK-016':  # 高雄銀行

            # last updated
            fx_data_time = BeautifulSoup(fx_item['last_updated'], features="lxml").get_text().strip()
            year, month, day = fx_data_time.split()[2].split('：')[1].split('/')
            fx_item['last_updated'] = "{}-{}-{}".format(year, month, day)

            # currency table
            fx_tr_list = BeautifulSoup(fx_item['currency_dict'], features="lxml").findAll('tr')
            fx_item['currency_dict'] = {}

            for fx_tr in fx_tr_list:

                # Currrency Code(CC), Telegraphic Transfer(TT), Bank Buy(BB), Bank Sell(BS)

                cc, bb_tt, bs_tt, bb_cash, bs_cash = [ fx_td.get_text() for fx_td in fx_tr.findAll('td') ]
                cc = cc.split()[0].strip()

                fx_item['currency_dict'][cc] = {
                    'bb_tt':self.format_fx(bb_tt), 'bs_tt':self.format_fx(bs_tt),
                    'bb_cash':self.format_fx(bb_cash), 'bs_cash':self.format_fx(bs_cash)
                }


        elif fx_item['bank'] == 'MBBTTWTP-050':  # 台灣企銀

            # last updated
            match = re.search('.*:(\d+)\/(\d+)\/(\d+) (\d+):(\d+)', fx_item['last_updated'])
            year, month, day, hour, minute = match.group(1, 2, 3, 4, 5)
            fx_item['last_updated'] = "{}-{}-{} {}:{}".format(int(year)+1911, month, day, hour, minute)

            # currency table
            fx_tr_list = BeautifulSoup(fx_item['currency_dict'], features="lxml").findAll('tr')
            fx_item['currency_dict'] = defaultdict(lambda:{'bb_cash':'-', 'bs_cash':'-', 'bb_tt':'-', 'bs_tt':':'})

            for fx_tr in fx_tr_list:

                # Currrency Code(CC), Telegraphic Transfer(TT), Bank Buy(BB), Bank Sell(BS)

                fx_cc = self.currency2id[fx_tr.find('th').get_text().strip()]
                fx_type, fx_bb, fx_bs = [ td_bs.get_text().strip() for td_bs in fx_tr.findAll('td') ]

                if 'CASH' == fx_type:
                    fx_item['currency_dict'][fx_cc]['bb_cash'] = self.format_fx(fx_bb)
                    fx_item['currency_dict'][fx_cc]['bs_cash'] = self.format_fx(fx_bs)
                elif 'SPOT' == fx_type:
                    fx_item['currency_dict'][fx_cc]['bb_tt'] = self.format_fx(fx_bb)
                    fx_item['currency_dict'][fx_cc]['bs_tt'] = self.format_fx(fx_bs)
                else:
                    continue


        elif fx_item['bank'] == 'SCBLTWTP-052':  # 渣打

            # last updated
            fx_item['last_updated'] = datetime.strptime(fx_item['last_updated'].strip(), 'Time of enquiry:%Y/%m/%d %H:%M:%S') \
                .strftime("%Y-%m-%d %H:%M")

            # currency table
            fx_tr_list = BeautifulSoup(fx_item['currency_dict'], features="lxml").findAll('tr')[1:]
            fx_item['currency_dict'] = {}

            for fx_tr in fx_tr_list:

                # Currrency Code(CC), Telegraphic Transfer(TT), Bank Buy(BB), Bank Sell(BS)

                cc = fx_tr.find('th').get_text().strip()
                bb_cash, bs_cash, bb_tt, bs_tt = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]

                fx_item['currency_dict'][cc] = {
                    'bb_tt':self.format_fx(bb_tt), 'bs_tt':self.format_fx(bs_tt),
                    'bb_cash':self.format_fx(bb_cash), 'bs_cash':self.format_fx(bs_cash)
                }


        elif fx_item['bank'] == 'TNBBTWTN-054':  # 京城

            # last updated
            last_updated_bs = BeautifulSoup(fx_item['last_updated'], features="lxml").findAll('p')
            year, month, day = re.search('.*：(.*)\/(.*)\/(.*)', last_updated_bs[0].get_text()).group(1,2,3)
            hour, minute = re.search('.*：(.*)：(.*)', last_updated_bs[1].get_text()).group(1,2)
            fx_item['last_updated'] = "{}-{}-{} {}:{}".format(int(year)+1911, month, day, hour, minute)

            # currency table
            fx_tr_list = BeautifulSoup(fx_item['currency_dict'], features="lxml").findAll('tr')[2:-2]
            fx_item['currency_dict'] = {}

            for fx_tr in fx_tr_list:

                # Currrency Code(CC), Telegraphic Transfer(TT), Bank Buy(BB), Bank Sell(BS)

                cc, bb_tt, bs_tt, bb_cash, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td')[1:] ]

                fx_item['currency_dict'][cc] = {
                    'bb_tt':self.format_fx(bb_tt), 'bs_tt':self.format_fx(bs_tt),
                    'bb_cash':self.format_fx(bb_cash), 'bs_cash':self.format_fx(bs_cash)
                }


        elif fx_item['bank'] == 'SUNYTWTP-108':  # 陽信

            # last updated
            fx_item['last_updated'] = datetime.strptime(fx_item['last_updated'].strip(), '資料更新時間：%Y/%m/%d %H:%M:%S') \
                .strftime("%Y-%m-%d %H:%M")

            # currency table
            fx_tr_list = BeautifulSoup(fx_item['currency_dict'], features="lxml").findAll('tr')
            fx_item['currency_dict'] = {}

            for fx_tr in fx_tr_list:

                # Currrency Code(CC), Telegraphic Transfer(TT), Bank Buy(BB), Bank Sell(BS)

                cc = self.currency2id[ fx_tr.find('td').findAll('span')[-1].get_text().strip() ]
                bb_cash, bs_cash, bb_tt, bs_tt = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td')[1:] ]

                fx_item['currency_dict'][cc] = {
                    'bb_tt':self.format_fx(bb_tt), 'bs_tt':self.format_fx(bs_tt),
                    'bb_cash':self.format_fx(bb_cash), 'bs_cash':self.format_fx(bs_cash)
                }


        elif fx_item['bank'] == 'ENTITWTP-816':  # 安泰

            # last updated
            match = re.search('.*: (\d+)\/(\d+)\/(\d+) (\d+):(\d+):(\d+) ', fx_item['last_updated'])
            year, month, day, hour, minute = match.group(1, 2, 3, 4, 5)
            fx_item['last_updated'] = "{}-{}-{} {}:{}".format(int(year)+1911, month, day, hour, minute)

            # currency table
            fx_tr_list = BeautifulSoup(fx_item['currency_dict'], features="lxml").findAll('tr')[1:]
            fx_item['currency_dict'] = {}

            for fx_tr in fx_tr_list:

                # Currrency Code(CC), Telegraphic Transfer(TT), Bank Buy(BB), Bank Sell(BS)

                cc, bb_tt, bs_tt, bb_cash, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]
                cc = cc.split()[-1].strip()

                fx_item['currency_dict'][cc] = {
                    'bb_tt':self.format_fx(bb_tt), 'bs_tt':self.format_fx(bs_tt),
                    'bb_cash':self.format_fx(bb_cash), 'bs_cash':self.format_fx(bs_cash)
                }


        elif fx_item['bank'] == 'JSIBTWTP-815':  # 日盛

            # last updated
            fx_date, fx_tp, fx_time = fx_item['last_updated'].split()
            year, month, day = fx_date.split('/')
            hour, minute, _ = fx_time.split(':')
            hour = int(hour)+12 if ('下午' == fx_tp) else int(hour)
            fx_item['last_updated'] = "{}-{}-{} {}:{}".format(year, month, day, hour, minute)

            # currency table
            fx_tr_list = BeautifulSoup(fx_item['currency_dict'], features="lxml").findAll('tr')[1:]
            fx_item['currency_dict'] = {}

            for fx_tr in fx_tr_list:

                # Currrency Code(CC), Telegraphic Transfer(TT), Bank Buy(BB), Bank Sell(BS)

                cc, bb_tt, bs_tt, bb_cash, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]
                cc = self.currency2id[cc]

                fx_item['currency_dict'][cc] = {
                    'bb_tt':self.format_fx(bb_tt), 'bs_tt':self.format_fx(bs_tt),
                    'bb_cash':self.format_fx(bb_cash), 'bs_cash':self.format_fx(bs_cash)
                }


        elif fx_item['bank'] == 'CDIBTWTP-809':  # 凱基

            # last updated
            match = re.search('.*: (\d+)\/(\d+)\/(\d+) (\d+):(\d+):(\d+)', fx_item['last_updated'])
            year, month, day, hour, minute = match.group(1, 2, 3, 4, 5)
            fx_item['last_updated'] = "{}-{}-{} {}:{}".format(year, month, day, hour, minute)

            # currency table
            fx_tr_list = BeautifulSoup(fx_item['currency_dict'], features="lxml").findAll('tr')[2:]
            fx_item['currency_dict'] = {}

            for fx_tr in fx_tr_list:

                # Currrency Code(CC), Telegraphic Transfer(TT), Bank Buy(BB), Bank Sell(BS)

                cc, _, bb_tt, bs_tt, bb_cash, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td')[:6] ]

                fx_item['currency_dict'][cc] = {
                    'bb_tt':self.format_fx(bb_tt), 'bs_tt':self.format_fx(bs_tt),
                    'bb_cash':self.format_fx(bb_cash), 'bs_cash':self.format_fx(bs_cash)
                }


        elif fx_item['bank'] == 'SINOTWTP-807':  # 永豐

            # last updated
            fx_item['last_updated'] = datetime.strptime(fx_item['last_updated'].strip(), '%Y-%m-%d %H:%M:%S') \
                .strftime("%Y-%m-%d %H:%M")

            # currency table
            fx_tr_list = BeautifulSoup(fx_item['currency_dict'], features="lxml").findAll('tr')[2:]
            fx_item['currency_dict'] = {}

            for fx_tr in fx_tr_list:

                # Currrency Code(CC), Telegraphic Transfer(TT), Bank Buy(BB), Bank Sell(BS)

                cc = re.search('.*\((.+?)\).*', fx_tr.find('td').find('div').get_text().strip()).group(1).strip()
                bb_tt, bs_tt, bb_cash, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td')[1:] ]

                fx_item['currency_dict'][cc] = {
                    'bb_tt':self.format_fx(bb_tt), 'bs_tt':self.format_fx(bs_tt),
                    'bb_cash':self.format_fx(bb_cash), 'bs_cash':self.format_fx(bs_cash)
                }


        elif fx_item['bank'] == 'FEINTWTP-805':  # 遠銀

            # last updated
            fx_item['last_updated'] = datetime.today().strftime("%Y-%m-%d %H:%M")

            # currency table
            fx_tr_list = BeautifulSoup(fx_item['currency_dict'], features="lxml").find('div').findAll('div', recursive=False)[1:]
            fx_item['currency_dict'] = {}

            for fx_tr in fx_tr_list:

                # Currrency Code(CC), Telegraphic Transfer(TT), Bank Buy(BB), Bank Sell(BS)

                cc, bb_tt, bs_tt, bb_cash, bs_cash = [ fx_td.find('span').find('span').get_text() for fx_td in fx_tr.findAll('div')[:-1] ]
                cc = cc.split()[1].strip()

                fx_item['currency_dict'][cc] = {
                    'bb_tt':self.format_fx(bb_tt), 'bs_tt':self.format_fx(bs_tt),
                    'bb_cash':self.format_fx(bb_cash), 'bs_cash':self.format_fx(bs_cash)
                }


        elif fx_item['bank'] == 'UBOTTWTP-803':  # 聯邦

            # last updated
            year, month, day, hour, minute = re.search('(\d*)\/(\d*)\/(\d*) (\d*):(\d*).*', fx_item['last_updated']).group(1,2,3,4,5)
            fx_item['last_updated'] = "{}-{}-{} {}:{}".format(int(year)+1911, month, day, hour, minute)

            # currency table
            fx_tr_list = BeautifulSoup(fx_item['currency_dict'], features="lxml").findAll('tr')[2:]
            fx_item['currency_dict'] = {}

            for fx_tr in fx_tr_list:

                # Currrency Code(CC), Telegraphic Transfer(TT), Bank Buy(BB), Bank Sell(BS)

                 #= self.currency2id[fx_tr.find('td').findAll('span')[-1].get_text().strip()]
                cc, bb_tt, bs_tt, bb_cash, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]
                cc = cc.split('/')[1].strip()

                fx_item['currency_dict'][cc] = {
                    'bb_tt':self.format_fx(bb_tt), 'bs_tt':self.format_fx(bs_tt),
                    'bb_cash':self.format_fx(bb_cash), 'bs_cash':self.format_fx(bs_cash)
                }


        elif fx_item['bank'] == 'COBKTWTP-147':  # 三信

            # last updated
            fx_time = BeautifulSoup(etree.tostring(fx_item['last_updated']), 'lxml').get_text().strip().split()
            year, month, day = fx_time[1].split('：')[1].split('/')
            hour, minute = fx_time[2].split(':')[:2]
            fx_item['last_updated'] = "{}-{}-{} {}:{}".format(int(year)+1911, month, day, hour, minute)

            # currency table
            fx_tr_list = BeautifulSoup(fx_item['currency_dict'], features="lxml").findAll('tr')[2:]
            fx_item['currency_dict'] = {}

            for fx_tr in fx_tr_list:

                # Currrency Code(CC), Telegraphic Transfer(TT), Bank Buy(BB), Bank Sell(BS)

                cc, bb_tt, bs_tt, bb_cash, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]
                cc = cc[-3:]

                fx_item['currency_dict'][cc] = {
                    'bb_tt':self.format_fx(bb_tt), 'bs_tt':self.format_fx(bs_tt),
                    'bb_cash':self.format_fx(bb_cash), 'bs_cash':self.format_fx(bs_cash)
                }


        elif fx_item['bank'] == 'BBBKTWTP-118':  # 板信

            # last updated
            fx_time = BeautifulSoup(etree.tostring(fx_item['last_updated']), features="lxml").get_text().strip().split()
            year, month, day = int(fx_time[1][4:-1])+1911, fx_time[2][:-1], fx_time[3][:-1]
            hour, minute = fx_time[5].split(':')[0], fx_time[5].split(':')[1]
            fx_item['last_updated'] = "{}-{}-{} {}:{}".format(year, month, day, hour, minute)

            # currency table
            fx_tr_list = BeautifulSoup(fx_item['currency_dict'], features="lxml").findAll('tr')[1:]
            fx_item['currency_dict'] = {}

            for fx_tr in fx_tr_list:

                # Currrency Code(CC), Telegraphic Transfer(TT), Bank Buy(BB), Bank Sell(BS)
                cc, bb_tt, bs_tt = [ fx_td.find('span').get_text().strip() for fx_td in fx_tr.findAll('td')[:3] ]
                bb_cash, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td')[3:] ]
                cc = self.currency2id[cc]

                fx_item['currency_dict'][cc] = {
                    'bb_tt':self.format_fx(bb_tt), 'bs_tt':self.format_fx(bs_tt),
                    'bb_cash':self.format_fx(bb_cash), 'bs_cash':self.format_fx(bs_cash)
                }


        elif fx_item['bank'] == 'HSBCTWTP-081':  # 匯豐

            # last updated
            fx_item['last_updated'] = datetime.strptime(fx_item['last_updated'].strip(), '匯率更新日期為 %Y/%m/%d') \
                .strftime("%Y-%m-%d")

            # currency table
            fx_tr_list = BeautifulSoup(fx_item['currency_dict'], features="lxml").findAll('tr')[3:]
            fx_item['currency_dict'] = {}

            for fx_tr in fx_tr_list:

                # Currrency Code(CC), Telegraphic Transfer(TT), Bank Buy(BB), Bank Sell(BS)

                cc_tmp, bb_tt, bs_tt, bb_cash, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]
                cc = re.search('.*\((.+?)\).*', cc_tmp).group(1)

                fx_item['currency_dict'][cc] = {
                    'bb_tt':self.format_fx(bb_tt), 'bs_tt':self.format_fx(bs_tt),
                    'bb_cash':self.format_fx(bb_cash), 'bs_cash':self.format_fx(bs_cash)
                }


        elif fx_item['bank'] == 'TCBBTWTH-053':  # 台中銀行

            # last updated
            fx_item['last_updated'] = datetime.strptime(fx_item['last_updated'].strip(), '查詢時間：%Y/%m/%d %H:%M:%S') \
                .strftime("%Y-%m-%d %H:%M")

            # currency table
            fx_tr_list = BeautifulSoup(fx_item['currency_dict'], features="lxml").findAll('tr')[1:]
            fx_item['currency_dict'] = {}

            for fx_tr in fx_tr_list:

                # Currrency Code(CC), Telegraphic Transfer(TT), Bank Buy(BB), Bank Sell(BS)
                cc, bb_cash, bs_cash, bb_tt, bs_tt = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]
                cc = cc.split()[1].strip()

                fx_item['currency_dict'][cc] = {
                    'bb_tt':self.format_fx(bb_tt), 'bs_tt':self.format_fx(bs_tt),
                    'bb_cash':self.format_fx(bb_cash), 'bs_cash':self.format_fx(bs_cash)
                }


        elif fx_item['bank'] == 'ICBCTWTP-017':  # 兆豐

            # last updated
            fx_data_time = BeautifulSoup(etree.tostring(fx_item['last_updated']), features="lxml").get_text().strip()
            year, month, day = fx_data_time.split()[1].split('/')
            hour, minute = fx_data_time.split()[3].split(':')
            fx_item['last_updated'] = "{}-{}-{} {}:{}".format(year, month, day, hour, minute)

            # currency table
            fx_tr_list = BeautifulSoup(fx_item['currency_dict'], features="lxml").findAll('tr')
            fx_item['currency_dict'] = {}

            for fx_tr in fx_tr_list:

                # Currrency Code(CC), Telegraphic Transfer(TT), Bank Buy(BB), Bank Sell(BS)

                cc_tmp, bb_tt, bb_cash, bs_tt, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td')[:-1] ]
                cc = re.search('.*\[(.+?)\].*', cc_tmp).group(1)

                fx_item['currency_dict'][cc] = {
                    'bb_tt':self.format_fx(bb_tt), 'bs_tt':self.format_fx(bs_tt),
                    'bb_cash':self.format_fx(bb_cash), 'bs_cash':self.format_fx(bs_cash)
                }


        elif fx_item['bank'] == 'SCSBTWTP-011':  # 上海

            # last updated
            fx_data_time = BeautifulSoup(etree.tostring(fx_item['last_updated']).strip(), features="lxml").get_text().strip()
            year, month, day, hour, minute = re.search('.*:\ *(\d*)\ *年\ *(\d*)\ *月\ *(\d*)\ *日\ *(\d*)\ *:\ *(\d*)\ *:\ *(\d*).*', fx_data_time).group(1,2,3,4,5)
            fx_item['last_updated'] = "{}-{}-{} {}:{}".format(int(year)+1911, month, day, hour, minute)

            # currency table
            fx_tr_list = BeautifulSoup(fx_item['currency_dict'], features="lxml").findAll('tr')[3:]
            _ = fx_tr_list.pop(2)
            fx_item['currency_dict'] = defaultdict(lambda:{'bb_cash':'-', 'bs_cash':'-', 'bb_tt':'-', 'bs_tt':':'})

            for fx_tr in fx_tr_list:

                # Currrency Code(CC), Telegraphic Transfer(TT), Bank Buy(BB), Bank Sell(BS)

                _, cc, bb, bs = [ fx_td.find('span').get_text().strip() for fx_td in fx_tr.findAll('td') ]

                if 'CASH' in cc:
                    cc = cc.split()[0]
                    fx_item['currency_dict'][cc]['bb_cash'] = self.format_fx(bb)
                    fx_item['currency_dict'][cc]['bs_cash'] = self.format_fx(bs)
                else:
                    fx_item['currency_dict'][cc]['bb_tt'] = self.format_fx(bb)
                    fx_item['currency_dict'][cc]['bs_tt'] = self.format_fx(bs)


        elif fx_item['bank'] == 'CCBCTWTP-009':  # 彰銀

            # last updated
            fx_item['last_updated'] = datetime.strptime(fx_item['last_updated'].split('/')[0].strip(), '更新時間: %Y-%m-%d %H:%M:%S') \
                .strftime("%Y-%m-%d %H:%M")

            # currency table
            fx_tr_list = BeautifulSoup(fx_item['currency_dict'], features="lxml").findAll('tr')
            fx_item['currency_dict'] = defaultdict(lambda:{'bb_cash':'-', 'bs_cash':'-', 'bb_tt':'-', 'bs_tt':':'})

            for fx_tr in fx_tr_list:

                # Currrency Code(CC), Telegraphic Transfer(TT), Bank Buy(BB), Bank Sell(BS)

                cc_tmp, bb, bs = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]
                cc = re.search('.*\((.+?)\).*', cc_tmp).group(1).strip()

                if '-C' in cc_tmp:
                    cc = cc[:3]
                    fx_item['currency_dict'][cc]['bb_cash'] = self.format_fx(bb)
                    fx_item['currency_dict'][cc]['bs_cash'] = self.format_fx(bs)
                else:
                    fx_item['currency_dict'][cc]['bb_tt'] = self.format_fx(bb)
                    fx_item['currency_dict'][cc]['bs_tt'] = self.format_fx(bs)


        elif fx_item['bank'] == 'HNBKTWTP-008':  # 華南

            # last updated
            fx_item['last_updated'] = datetime.strptime(fx_item['last_updated'].strip(), 'Generated At: %Y/%m/%d %H:%M:%S') \
                .strftime("%Y-%m-%d %H:%M")

            # currency table
            fx_tr_list = BeautifulSoup(fx_item['currency_dict'], features="lxml").findAll('tr')
            fx_item['currency_dict'] = defaultdict(lambda:{'bb_cash':'-', 'bs_cash':'-', 'bb_tt':'-', 'bs_tt':':'})

            for fx_tr in fx_tr_list:

                # Currrency Code(CC), Telegraphic Transfer(TT), Bank Buy(BB), Bank Sell(BS)

                cc_tmp, bb, bs = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]
                cc = cc_tmp.split()[0].strip()

                if 'CASH' in cc_tmp:
                    fx_item['currency_dict'][cc]['bb_cash'] = self.format_fx(bb)
                    fx_item['currency_dict'][cc]['bs_cash'] = self.format_fx(bs)
                else:
                    fx_item['currency_dict'][cc]['bb_tt'] = self.format_fx(bb)
                    fx_item['currency_dict'][cc]['bs_tt'] = self.format_fx(bs)


        elif fx_item['bank'] == 'FCBKTWTP-007':  # 第一銀

            # last updated
            fx_item['last_updated'] = BeautifulSoup(etree.tostring(fx_item['last_updated']), features="lxml").get_text().strip()
            fx_item['last_updated'] = datetime.strptime(fx_item['last_updated'], '( Data effect date ： %Y/%m/%d %H:%M:%S )') \
                .strftime("%Y-%m-%d %H:%M")

            # currency table
            fx_tr_list = BeautifulSoup(fx_item['currency_dict'], features="lxml").findAll('tr')[1:-1]
            fx_item['currency_dict'] = defaultdict(lambda:{'bb_cash':'-', 'bs_cash':'-', 'bb_tt':'-', 'bs_tt':':'})

            for fx_tr in fx_tr_list:

                # Currrency Code(CC), Telegraphic Transfer(TT), Bank Buy(BB), Bank Sell(BS)

                cc_tmp, fx_type, bb, bs = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td')[:4] ]

                if '(' in cc_tmp:
                    cc = re.search('.*\((.+?)\).*', cc_tmp).group(1).strip()

                if fx_type == 'Cash':
                    fx_item['currency_dict'][cc]['bb_cash'] = self.format_fx(bb)
                    fx_item['currency_dict'][cc]['bs_cash'] = self.format_fx(bs)
                else:
                    fx_item['currency_dict'][cc]['bb_tt'] = self.format_fx(bb)
                    fx_item['currency_dict'][cc]['bs_tt'] = self.format_fx(bs)


        elif fx_item['bank'] == 'CTCBTWTP-822':  # 中國信託

            # last updated
            fx_item['last_updated'] = datetime.strptime(fx_item['last_updated'].strip(), '出表時間：%Y/%m/%d  %H:%M:%S') \
                .strftime("%Y-%m-%d %H:%M")

            # currency table
            fx_tr_list = BeautifulSoup(fx_item['currency_dict'], features="lxml").findAll('tr')[1:]
            fx_item['currency_dict'] = {}

            for fx_tr in fx_tr_list:

                # Currrency Code(CC), Telegraphic Transfer(TT), Bank Buy(BB), Bank Sell(BS)

                cc, bb_cash, bs_cash, bb_tt, bs_tt = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]
                cc = cc.split('/')[1].strip()

                fx_item['currency_dict'][cc] = {
                    'bb_tt':self.format_fx(bb_tt), 'bs_tt':self.format_fx(bs_tt),
                    'bb_cash':self.format_fx(bb_cash), 'bs_cash':self.format_fx(bs_cash)
                }


        elif fx_item['bank'] == 'TSIBTWTP-812':  # 台新

            # last updated
            fx_item['last_updated'] = datetime.strptime(fx_item['last_updated'].strip(), '更新時間 : %Y/%m/%d  %H:%M:%S') \
                .strftime("%Y-%m-%d %H:%M")

            # currency table
            fx_tr_list = BeautifulSoup(fx_item['currency_dict'], features="lxml").findAll('tr')[1:]
            fx_item['currency_dict'] = {}

            for fx_tr in fx_tr_list:

                # Currrency Code(CC), Telegraphic Transfer(TT), Bank Buy(BB), Bank Sell(BS)

                cc, bb_tt, bs_tt, bb_cash, bs_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td') ]
                cc = cc.strip()[-3:].strip()

                fx_item['currency_dict'][cc] = {
                    'bb_tt':self.format_fx(bb_tt), 'bs_tt':self.format_fx(bs_tt),
                    'bb_cash':self.format_fx(bb_cash), 'bs_cash':self.format_fx(bs_cash)
                }


        elif fx_item['bank'] == 'MKTBTWTP-103':  # 新光

            # last updated
            fx_item['last_updated'] = datetime.strptime(fx_item['last_updated'].strip(), '%Y-%m-%d %H:%M:%S') \
                .strftime("%Y-%m-%d %H:%M")

            # currency table
            fx_tr_list = BeautifulSoup(fx_item['currency_dict'], features="lxml").findAll('ul')[1:]
            fx_item['currency_dict'] = {}

            for fx_tr in fx_tr_list:

                # Currrency Code(CC), Telegraphic Transfer(TT), Bank Buy(BB), Bank Sell(BS)

                cc, _, bb_tt, bs_tt, bb_cash, bs_cash, _ = [ fx_td.find('p').get_text().strip() for fx_td in fx_tr.findAll('li') ]

                fx_item['currency_dict'][cc] = {
                    'bb_tt':self.format_fx(bb_tt), 'bs_tt':self.format_fx(bs_tt),
                    'bb_cash':self.format_fx(bb_cash), 'bs_cash':self.format_fx(bs_cash)
                }


        elif fx_item['bank'] == 'LBOTTWTP-005': # 土地

            # last updated
            fx_item['last_updated'] = datetime.strptime(fx_item['last_updated'].strip(), '更新時間：%Y/%m/%d %H:%M:%S') \
                .strftime("%Y-%m-%d %H:%M")

            # currency table
            fx_tr_list = BeautifulSoup(fx_item['currency_dict'], features="lxml").findAll('tr')
            fx_item['currency_dict'] = {}

            for fx_tr in fx_tr_list:

                # Currrency Code(CC), Telegraphic Transfer(TT), Bank Buy(BB), Bank Sell(BS)

                cc_tmp, bb_tt, bs_tt, bb_cash, bs_cash = fx_tr.findAll('td')[:5]
                cc = re.search('.*\((.+?)\).*', cc_tmp.find('label').get_text()).group(1).strip()

                fx_item['currency_dict'][cc] = {
                    'bb_tt':self.format_fx(bb_tt.find('div').get_text()), 'bs_tt':self.format_fx(bs_tt.find('div').get_text()),
                    'bb_cash':self.format_fx(bb_cash.find('div').get_text()), 'bs_cash':self.format_fx(bs_cash.find('div').get_text())
                }


        elif fx_item['bank'] == 'SINOTWTP-700': # 中郵

            # last updated
            year, month, day = fx_item['last_updated'].split()[1].split('/')
            fx_item['last_updated'] = "{}-{}-{}".format(int(year)+1911, month, day)

            # currency table
            fx_tr_list = BeautifulSoup(fx_item['currency_dict'], features="lxml") \
                .find('div', {'id':'css_table1'}).findAll('div', recursive=False)[1:]
            fx_item['currency_dict'] = {}

            for fx_tr in fx_tr_list:

                # Currrency Code(CC), Telegraphic Transfer(TT), Bank Buy(BB), Bank Sell(BS)

                cc_tmp, bb_tt, bb_cash, bs_tt, bs_cash = fx_tr.findAll('div')
                cc = re.search('.*\((.+?)\).*', cc_tmp.get_text()).group(1).strip()

                fx_item['currency_dict'][cc] = {
                    'bb_tt':self.format_fx(bb_tt.get_text()), 'bs_tt':self.format_fx(bs_tt.get_text()),
                    'bb_cash':self.format_fx(bb_cash.get_text()), 'bs_cash':self.format_fx(bs_cash.get_text())
                }


        elif fx_item['bank'] == 'CITITWTX-021':  # 花旗

            # last updated
            fx_item['last_updated'] = datetime.today().strftime("%Y-%m-%d")

            # currency table
            fx_tr_list = BeautifulSoup(fx_item['currency_dict'], features="lxml").findAll('tr')[2:]
            fx_item['currency_dict'] = {}

            for fx_tr in fx_tr_list:

                # Currrency Code(CC), Telegraphic Transfer(TT), Bank Buy(BB), Bank Sell(BS)

                cc, bs_tt, bb_tt, bs_cash, bb_cash = [ fx_td.get_text().strip() for fx_td in fx_tr.findAll('td')[1:] ]

                fx_item['currency_dict'][cc] = {
                    'bb_tt':self.format_fx(bb_tt), 'bs_tt':self.format_fx(bs_tt),
                    'bb_cash':self.format_fx(bb_cash), 'bs_cash':self.format_fx(bs_cash)
                }


        return fx_item
