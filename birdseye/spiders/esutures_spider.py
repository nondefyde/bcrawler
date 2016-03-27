import json
import scrapy
from birdseye.items import BirdseyeItem


class XsupplySpider(scrapy.Spider):
    name = "esu"
    allowed_domains = ["esutures.com"]
    start_urls = ['https://www.esutures.com/product/0-in-date/']

    def parse(self, response):
        urls = response.css('ul.brands li a::attr(href)').extract()
        manufacturers = response.css('ul.brands li a::text').extract()
        for num in range(len(urls)):
            url = urls[num]
            item = BirdseyeItem()
            item['url'] = 'https://www.esutures.com' + url.strip()
            item['manufacturer'] = manufacturers[num]
            item['vendor'] = 'www.esutures.com'
            request = scrapy.Request(item['url'], callback=self.parse_type, meta={'item': item})
            yield request

    def parse_type(self, response):

        item = response.meta['item']
        urls = response.css('ul.brands li a::attr(href)').extract()
        types = response.css('ul.brands li a::text').extract()
        for num in range(len(urls)):
            url = urls[num]
            item['product_name'] = types[num]
            item['flag'] = ""
            item['url'] = 'https://www.esutures.com' + url.strip()
            request = scrapy.Request(item['url'], callback=self.parse_event, meta={'item': item})
            yield request

    def parse_event(self, response):
        print response.request.url
        item = response.meta['item']

        sel = response.css('html')
        counts = sel.css('div#products h4').extract()
        if len(counts) > 0 and item['flag'] == "":
            for index in range(1,len(counts)+1):
                url = response.request.url+"?open=%s" % +index
                item['flag'] = "true"
                print url
                request = scrapy.Request(url, callback=self.parse_event, meta={'item': item})
                yield request
        else:
            oems = sel.css('div.itn a::text').extract()
            product_urls = sel.css('div.itn a::attr(href)').extract()
            prices = sel.css('div.prc span::text').extract()
            descriptions = sel.css('div.pt a::text').extract()
            stock_quantities = sel.css('div.pt::text').extract()
            for num in range(len(oems)):
                item['oem'] = oems[num]
                item['price'] = prices[num]
                item['product_url'] = 'https://www.esutures.com' + product_urls[num]
                item['description'] = descriptions[num]
                item['stock_quantity'] = stock_quantities[num]
                yield item