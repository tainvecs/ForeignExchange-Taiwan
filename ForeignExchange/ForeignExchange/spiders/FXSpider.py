# -*- coding: utf-8 -*-

import scrapy
from ForeignExchange.items import ForeignexchangeItem as FXItem

import json


BANK_TABLE_PATH = './res/bank_table.json'


class FXSpider(scrapy.Spider):

    name = 'fx_spider'

    def start_requests(self):

        with open(BANK_TABLE_PATH, 'r') as in_file:
            bank_table = json.load(in_file)

        return [ scrapy.Request(url=bank_table[bank_id]['start_link'], callback=self.parse_items, meta=bank_table[bank_id])
            for bank_id in bank_table ]


    def parse_items(self, response):

        fx_item = FXItem()
        fx_item['bank'] = response.meta.get('bank_id')

        last_updated_xpath = response.meta.get('last_updated_xpath')
        table_xpath = response.meta.get('fx_table_xpath')

        if not last_updated_xpath:
            fx_item['last_updated'] = None
        else:
            fx_item['last_updated'] = response.xpath(last_updated_xpath).extract_first()

        if not table_xpath:
            fx_item['currency_dict'] = None
        else:
            fx_item['currency_dict'] = response.xpath(table_xpath).extract_first()

        return fx_item
