# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BirdseyeItem(scrapy.Item):
    vendor = scrapy.Field()
    url = scrapy.Field()
    product_name = scrapy.Field()
    description = scrapy.Field()
    manufacturer = scrapy.Field()
    oem = scrapy.Field()
    price = scrapy.Field()
    stock_quantity = scrapy.Field()
    product_url = scrapy.Field()

    pass