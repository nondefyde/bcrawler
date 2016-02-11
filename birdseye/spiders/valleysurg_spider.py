import json
import scrapy
from birdseye.items import BirdseyeItem

class ValleysurgSpider(scrapy.Spider):
    name = "valley"
    allowed_domains = ["valleysurg.com"]
    start_urls = ["https://www.valleysurg.com"]

    def parse(self, response):
        urls = response.css('ul.category-list li.has-no-children a::attr(href)').extract()
        for num in range(len(urls)):
            url = urls[num].strip()
            item = BirdseyeItem()
            item['url'] = "https://www.valleysurg.com"+url
            item['vendor'] = 'http://www.valleysurg.com'
            item['manufacturer'] = url[1:]
            request = scrapy.Request(item['url'], callback=self.parse_data, meta={'item': item})
            yield request

    def parse_data(self, response):
        sel = response.css('body')
        temp = response.meta['item']

        product_names = sel.css('h2.product-name a::text').extract()
        product_urls = sel.css('h2.product-name a::attr(href)').extract()
        prices = sel.css('div.price-box span.regular-price span::text').extract()
        oem = sel.css('div.ratings div::text').extract()

        for n in range(0, len(product_names)):
            item = BirdseyeItem()
            item['product_name'] = product_names[n]
            item['oem'] = oem[n].strip()
            item['product_url'] = product_urls[n]
            item['price'] = prices[n]
            item['url'] = temp['url']
            item['vendor'] = temp['vendor']
            item['manufacturer'] = temp['manufacturer']
            request = scrapy.Request(item['product_url'], callback=self.parse_detail, meta={'item': item})
            yield request

        pagination_lists = sel.css('div.pages ol li.current + li a::attr(href)').extract()
        pagination_lists = list(set(pagination_lists))
        print pagination_lists
        if len(pagination_lists) > 0:
            request = scrapy.Request(pagination_lists[0], callback=self.parse_data, meta={'item': temp})
            yield request

    def parse_detail(self, response):
        sel = response.css('body')
        item = response.meta['item']
        item['stock_quantity'] = sel.css('p.availability span::text').extract()[0]
        description = sel.css('div.panel-body div.std::text').extract()
        if len(description) > 0:
            item['description'] = description[0].strip()
        yield item