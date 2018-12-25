# -*- coding: utf-8 -*-

import scrapy
from ForeignExchange.items import ForeignexchangeItem as FXItem

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
from lxml import etree


CHROME_DRIVER_PATH = './bin/chromedriver'


class FXSpider(scrapy.Spider):

    name = 'fx_spider'

    def start_requests(self):

        urls = [
            'https://rate.bot.com.tw/xrt',  # 台灣銀行
            'https://www.esunbank.com.tw/bank/personal/deposit/rate/forex/foreign-exchange-rates',  # 玉山
            'https://www.o-bank.com/zh-tw/retail/cm/ratemain/cm-fxrate',  # 王道
            'https://www.dbs.com.tw/personal/rates/foreign-exchange-rates.page',  # 星展
            'https://www.yuantabank.com.tw/bank/exchangeRate/hostccy.do',  # 元大
            'https://www.fubon.com/Fubon_Portal/banking/Personal/deposit/exchange_rate/exchange_rate1.jsp',  # 富邦
            'https://www.cathaybk.com.tw/cathaybk/personal/exchange/product/currency-billboard/#first-tab-01',  # 國泰
            'https://www.tcb-bank.com.tw/finance_info/Pages/foreign_spot_rate.aspx',  # 合庫
            'https://ibank.bok.com.tw/PIB/ca/ca02102/CA02102_HOME.xhtml',  # 高雄銀行
            'https://www.tbb.com.tw/exchange_rate_eng',  # 台灣企銀
            'https://service.standardchartered.com.tw/en/check/inquiry-rate-foreign-exchange-en.asp',  # 渣打
            'https://customer.ktb.com.tw/new/personal/interest_rate_inquire?utm_source=www&utm_medium=quick&utm_campaign=rate',  # 京城
            'https://service.sunnybank.com.tw/portal/pt/pt02003/PT02003Index.xhtml',  # 陽信
            'http://www.entiebank.com.tw/rate/page_host.asp',  # 安泰
            'http://rate.jihsunbank.com.tw/Rate/ExgRate.htm',  # 日盛
            'https://www.kgibank.com/T01/T0111/rate03.jsp',  # 凱基
            'https://bank.sinopac.com/MMA8/bank/html/rate/bank_ExchangeRate.html',  # 永豐
            'https://www.feib.com.tw/rateList',  # 遠銀
            'https://mybank.ubot.com.tw/LoadAP/LoadAP?aptype=IBANK&pageid=IP0907300',  # 聯邦
            'https://www.cotabank.com.tw/web/interest_3/', # 三信
            'http://www.bop.com.tw/bankinfo/BS1003.aspx',  # 板信
            'https://www.hsbc.com.tw/1/2//Misc/popup-tw/currency-calculator/',  # 匯豐
            'https://ibank.tcbbank.com.tw/PIB/cb5/cb501005/CB501005_01.faces',  # 台中銀行
            'https://wwwfile.megabank.com.tw/other/bulletin02_02.asp',  # 兆豐
            'https://ibank.scsb.com.tw/netbank.portal?_nfpb=true&_pageLabel=page_other12&_nfls=false',  # 上海
            'https://www.bankchb.com/frontend/G0100_query.jsp',  # 彰銀
            'http://www.hncb.com.tw/wps/portal/eng/services/foreign_exchange_rates/',  # 華南
            'https://ibank.firstbank.com.tw/NetBank/7/0201.html',  # 第一銀
            'https://www.ctbcbank.com/CTCBPortalWeb/toPage?id=TW_RB_CM_ebank_018001',  # 中國信託
            'https://www.taishinbank.com.tw/TS/TS06/TS0605/TS060502/index.htm?urlPath1=TS02&urlPath2=TS0202',  # 台新
            'https://www.skbank.com.tw/rate.html',  # 新光
            'https://mybank.landbank.com.tw/Sign/SIGN_finf_01/Index',  # 土地
            'https://ipost.post.gov.tw/pst/home.html',  # 中郵
            'https://www.citibank.com.tw/sim/index.htm',  # 花旗
        ]

        banks_id = [
            'BKTWTWTP-004',  # 台灣銀行
            'ESUNTWTP-808',  # 玉山
            'IBOTTWTP-048',  # 王道
            'DBSSTWTP-810',  # 星展
            'APBKTWTH-806',  # 元大
            'TPBKTWTP-012',  # 富邦
            'UWCBTWTP-013',  # 國泰
            'TACBTWTP-006',  # 合庫
            'BKAOTWTK-016',  # 高雄銀行
            'MBBTTWTP-050',  # 台灣企銀
            'SCBLTWTP-052',  # 渣打
            'TNBBTWTN-054',  # 京城
            'SUNYTWTP-108',  # 陽信
            'ENTITWTP-816',  # 安泰
            'JSIBTWTP-815',  # 日盛
            'CDIBTWTP-809',  # 凱基
            'SINOTWTP-807',  # 永豐
            'FEINTWTP-805',  # 遠銀
            'UBOTTWTP-803',  # 聯邦
            'COBKTWTP-147',  # 三信
            'BBBKTWTP-118',  # 板信
            'HSBCTWTP-081',  # 匯豐
            'TCBBTWTH-053',  # 台中銀行
            'ICBCTWTP-017',  # 兆豐
            'SCSBTWTP-011',  # 上海
            'CCBCTWTP-009',  # 彰銀
            'HNBKTWTP-008',  # 華南
            'FCBKTWTP-007',  # 第一銀
            'CTCBTWTP-822',  # 中國信託
            'TSIBTWTP-812',  # 台新
            'MKTBTWTP-103',  # 新光
            'LBOTTWTP-005',  # 土地
            'SINOTWTP-700',  # 中郵
            'CITITWTX-021',  # 花旗
        ]

        return [ scrapy.Request(url=url, callback=self.parse_items, meta={'url':url, 'bank_id':bank_id})
            for url,bank_id in zip(urls,banks_id) ]

        #return [ scrapy.Request(url=urls[2], callback=self.parse_items, meta={'url':urls[2], 'bank_id':banks_id[2]}) ]


    def parse_items(self, response):

        url = response.meta.get('url')
        bank_id = response.meta.get('bank_id')
        js_spider = False

        if bank_id == 'BKTWTWTP-004':    # 台灣銀行
            last_updated_xpath = '/html/body/div[1]/main/div[3]/p[2]/span[2]//text()'
            table_xpath = '/html/body/div[1]/main/div[3]/table/tbody'
        elif bank_id == 'ESUNTWTP-808':  # 玉山
            last_updated_xpath = '//*[@id="LbQuoteTime"]//text()'
            table_xpath = '//*[@id="inteTable1"]'
        elif bank_id == 'IBOTTWTP-048':  # 王道
            last_updated_xpath = '//*[@id="layout_0_tagMain"]/section/div[1]/div/div[2]/div/div[1]/span//text()'
            table_xpath = '//*[@id="layout_0_tagMain"]/section/div[1]/div/div[2]/div/div[3]'
        elif bank_id == 'DBSSTWTP-810':  # 星展
            last_updated_xpath = '/html/body/div[1]/div[4]/div[1]/div/div[3]/span[2]//text()'
            table_xpath = '/html/body/div[1]/div[4]/div[1]/div/table'
        elif bank_id == 'APBKTWTH-806':  # 元大
            last_updated_xpath = '//*[@id="contentPage"]/div[2]/div[1]/div/div[1]/div[1]/ul'
            table_xpath = '//*[@id="contentPage"]/div[2]/div[1]/div/div[2]/table[1]'
        elif bank_id == 'TPBKTWTP-012':  # 富邦
            last_updated_xpath = '//*[@id="financialInfo1Div"]/div[1]//text()'
            table_xpath = '//*[@id="financialInfo1Div"]/div[3]/table/tbody'
        elif bank_id == 'UWCBTWTP-013':  # 國泰
            last_updated_xpath = '//*[@id="layout_0_rightcontent_1_firsttab01_0_tab_rate_realtime"]/p//text()'
            table_xpath = '//*[@id="layout_0_rightcontent_1_firsttab01_0_tab_rate_realtime"]/table/tbody'
        elif bank_id == 'TACBTWTP-006':  # 合庫
            last_updated_xpath = '//*[@id="ctl00_PlaceHolderEmptyMain_PlaceHolderMain_fecurrentid_lblDate"]//text()'
            table_xpath = '//*[@id="ctl00_PlaceHolderEmptyMain_PlaceHolderMain_fecurrentid_gvResult"]'
        elif bank_id == 'BKAOTWTK-016':  # 高雄銀行
            last_updated_xpath = '//*[@id="formLink:refreshPanel"]/h2/span[2]'
            table_xpath = '//*[@id="formLink:datagrid1_data"]'
        elif bank_id == 'MBBTTWTP-050':  # 台灣企銀
            last_updated_xpath = '//*[@id="check_deposits"]/p[2]/text()[2]'
            table_xpath = '//*[@id="check_deposits"]/div/table/tbody'
        elif bank_id == 'SCBLTWTP-052':  # 渣打
            last_updated_xpath = '//*[@id="midpage"]/div[3]//text()'
            table_xpath = '//*[@id="innertable"]/table'
        elif bank_id == 'TNBBTWTN-054':  # 京城
            last_updated_xpath = '/html/body/div[2]/div[6]/div[3]/div[2]/div[2]/div[5]'
            table_xpath = '//*[@id="table152"]'
        elif bank_id == 'SUNYTWTP-108':  # 陽信
            last_updated_xpath = '//*[@id="form:mainBox_content"]/div/div[1]/span[2]//text()'
            table_xpath = '//*[@id="form:exRate_data"]'
        elif bank_id == 'ENTITWTP-816':  # 安泰
            click_xpaths = []
            last_updated_xpath = '/html/body/table[1]/tbody/tr/td/font//text()'
            table_xpath = '/html/body/table[3]/tbody'
            js_spider = True
        elif bank_id == 'JSIBTWTP-815':  # 日盛
            click_xpaths = []
            last_updated_xpath = '/html/body/center/table[1]/tbody/tr[5]/td/b/em//text()'
            table_xpath = '/html/body/center/table[2]/tbody/tr/td/table/tbody'
            js_spider = True
        elif bank_id == 'CDIBTWTP-809':  # 凱基
            click_xpaths = []
            last_updated_xpath = '//*[@id="main"]/div/div[3]/div[2]/div[3]/div[3]/div[2]/table/tbody/tr[1]/th//text()'
            table_xpath = '//*[@id="main"]/div/div[3]/div[2]/div[3]/div[3]/div[2]/table/tbody'
            js_spider = True
        elif bank_id == 'SINOTWTP-807':  # 永豐
            click_xpaths = []
            last_updated_xpath = '//*[@id="tab1_date"]//text()'
            table_xpath = '//*[@id="tab1"]/table/tbody'
            js_spider = True
        elif bank_id == 'FEINTWTP-805':  # 遠銀
            click_xpaths = []
            last_updated_xpath = None
            table_xpath = '//*[@id="exchangerateDiv"]'
            js_spider = True
        elif bank_id == 'UBOTTWTP-803':  # 聯邦
            click_xpaths = []
            last_updated_xpath = '/html/body/form/table/tbody/tr/td/table[1]/tbody/tr/td[2]/table/tbody/tr[2]/td/div/font/text()[2]'
            table_xpath = '/html/body/form/table/tbody/tr/td/table[2]/tbody'
            js_spider = True
        elif bank_id == 'COBKTWTP-147':  # 三信
            click_xpaths = []
            last_updated_xpath = '//*[@id="UpTime"]'
            table_xpath = '//*[@id="T1"]/tbody'
            js_spider = True
        elif bank_id == 'BBBKTWTP-118':  # 板信
            click_xpaths = []
            last_updated_xpath = '//*[@id="form1"]/div[3]/table[1]/tbody/tr[3]/td'
            table_xpath = '//*[@id="gvFxRate"]/tbody'
            js_spider = True
        elif bank_id == 'HSBCTWTP-081':  # 匯豐
            click_xpaths = []
            last_updated_xpath = '/html/body/div/div[4]/div[4]/div/div/div/form/table[2]/tbody/tr[1]/td[2]//text()'
            table_xpath = '/html/body/div/div[4]/div[4]/div/div/div/form/table[2]/tbody'
            js_spider = True
        elif bank_id == 'TCBBTWTH-053':  # 台中銀行
            click_xpaths = []
            last_updated_xpath = '//*[@id="formpop"]/div/div[2]/div[3]/table[1]/tbody/tr/td/span//text()'
            table_xpath = '//*[@id="formpop:datagrid_DataGridBody"]/tbody'
            js_spider = True
        elif bank_id == 'ICBCTWTP-017':  # 兆豐
            click_xpaths = []
            last_updated_xpath = '/html/body/div[2]/div[2]/div[1]/table[1]/tbody/tr'
            table_xpath = '//*[@id="contentTbody"]'
            js_spider = True
        elif bank_id == 'SCSBTWTP-011':  # 上海
            click_xpaths = []
            last_updated_xpath = '/html/body/div/div[2]/div/div/div/div/table/tbody/tr/td/div/div/div[2]/form/table[1]/tbody/tr/td/table[2]/tbody/tr[2]/td'
            table_xpath = '/html/body/div/div[2]/div/div/div/div/table/tbody/tr/td/div/div/div[2]/form/table[1]/tbody/tr/td/table[2]/tbody'
            js_spider = True
        elif bank_id == 'CCBCTWTP-009':  # 彰銀
            click_xpaths = []
            last_updated_xpath = '//*[@id="updatetime"]//text()'
            table_xpath = '//*[@id="mm-0"]/div[2]/div[2]/div[3]/div/div/div/div/div/div/div[2]/div[4]/table/tbody'
            js_spider = True
        elif bank_id == 'HNBKTWTP-008':  # 華南
            click_xpaths = ['//*[@id="container"]/div[2]/div/div[2]/div[3]/div[1]/div/div/div/div/div[1]/div/a/div/div/div']
            last_updated_xpath = '//*[@id="exRateDataTime"]//text()'
            table_xpath = '//*[@id="exRateBox"]'
            js_spider = True
        elif bank_id == 'FCBKTWTP-007':  # 第一銀
            click_xpaths = []
            last_updated_xpath = '/html/body/div'
            table_xpath = '//*[@id="table1"]/tbody'
            js_spider = True
        elif bank_id == 'CTCBTWTP-822':  # 中國信託
            click_xpaths = []
            last_updated_xpath = '//*[@id="pageForm:twdDiv"]/div/div/table[1]/tbody/tr[2]/td//text()'
            table_xpath = '//*[@id="mainTable"]/tbody'
            js_spider = True
        elif bank_id == 'TSIBTWTP-812':  # 台新
            click_xpaths = []
            last_updated_xpath = '/html/body/div/indexcontent/div[3]/table[1]/tbody/tr/td[2]/div/span/font//text()'
            table_xpath = '/html/body/div/indexcontent/div[3]/table[2]/tbody/tr[1]/td/table/tbody'
            js_spider = True
        elif bank_id == 'MKTBTWTP-103':  # 新光
            click_xpaths = []
            last_updated_xpath = '//*[@id="other"]/div[2]/ul[2]/li[7]/p//text()'
            table_xpath = '//*[@id="other"]/div[2]'
            js_spider = True
        elif bank_id == 'LBOTTWTP-005':  # 土地
            click_xpaths = []
            last_updated_xpath = '/html/body/section/div/div/div[2]/div[2]/div[2]//text()'
            table_xpath = '/html/body/section/div/div/div[2]/div[2]/table/tbody'
            js_spider = True
        elif bank_id == 'SINOTWTP-700':  # 中郵
            click_xpaths = ['//*[@id="noticeall"]/div[5]/div/div[1]/div[2]/ul/li[3]/a']
            last_updated_xpath = '//*[@id="css_table"]/div/div//text()'
            table_xpath = '//*[@id="css_table1"]'
            js_spider = True
        elif bank_id == 'CITITWTX-021':  # 花旗
            click_xpaths = ['//*[@id="header"]/div[1]/ul[2]/li[7]/a', '//*[@id="f1"]/table/tbody/tr[3]/td/table/tbody/tr[1]/td[2]/a']
            last_updated_xpath = None
            table_xpath = '//*[@id="f1"]/table[2]/tbody'
            js_spider = True


        if js_spider:

            options = webdriver.ChromeOptions()
            options.add_argument('headless')
            options.add_argument('window-size=1200,1100');
            options.add_argument('user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"')

            browser = webdriver.Chrome(CHROME_DRIVER_PATH, options=options)
            browser.get(url)

            for click_xpath in click_xpaths:
                WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.XPATH, click_xpath))
                ).click()
            time.sleep(1)
            response = browser.page_source
            browser.close()

            xml_tree = etree.HTML(response)

            #with open('tmp.html', 'w') as ofile:
            #    ofile.write(response)


        fx_item = FXItem()
        fx_item['bank'] = bank_id

        if not last_updated_xpath:
            fx_item['last_updated'] = None
        elif not js_spider:
            fx_item['last_updated'] = response.xpath(last_updated_xpath).extract_first()
        else:
            fx_item['last_updated'] = xml_tree.xpath(last_updated_xpath)[0]

        if not table_xpath:
            fx_item['currency_dict'] = None
        elif not js_spider:
            fx_item['currency_dict'] = response.xpath(table_xpath).extract_first()
        else:
            fx_item['currency_dict'] = etree.tostring(xml_tree.xpath(table_xpath)[0])

        return fx_item
