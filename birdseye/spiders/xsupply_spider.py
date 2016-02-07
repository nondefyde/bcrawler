import json
import scrapy
from birdseye.items import BirdseyeItem


class XsupplySpider(scrapy.Spider):
    name = "xsupply"
    allowed_domains = ["xs-supply.com"]
    start_urls = ['http://www.xs-supply.com/product-list.html']

    def parse(self, response):
        urls = response.css('ul#nav li.level-1 a::attr(href)').extract()
        manufacturers = response.css('ul#nav li.level-1 a::text').extract()
        for num in range(len(urls)):
            url = urls[num]
            item = BirdseyeItem()
            item['url'] = url.strip()
            # item['manufacturer'] = manufacturers[num]
            # item['vendor'] = 'http://www.xs-supply.com/'
            request = scrapy.Request(item['url'], callback=self.parse_url, meta={'item': item})
            yield request
            break

    def parse_url(self, response):

        item = response.meta['item']

        urls = response.css('div.item-image a::attr(href)').extract()
        prices = response.css('div.item-price::text').extract()
        quantities = response.css('p#inventory-message::text').extract()
        oems = response.css('div.item-details h5 a::text').extract()
        for num in range(len(urls)):
            url = urls[num]
            item['url'] = url.strip()
            item['price'] = (prices[num]).strip()
            item['stock_quantity'] = quantities[num]
            item['product_url'] = url.strip()
            item['product_name'] = ''
            item['oem'] = oems[num]
            # print item
            # request = scrapy.Request(item['product_url'], callback=self.description, meta={'item': item})
            yield item

        paging = response.css('span.current + a::attr(href)').extract()
        if len(paging) > 0:
            next_page = paging[0].strip()
            request = scrapy.Request(next_page, callback=self.parse_url, meta={'item': item})
            yield request

    def description(self, response):
        item = response.meta['item']
        # item['description'] = ''
        # description = response.css('h5.title + div.col-md-13').extract()
        # if len(description) > 0:
        #     item['description'] = description[0]
        yield item