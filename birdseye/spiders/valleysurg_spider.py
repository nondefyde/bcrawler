import json
import scrapy
from birdseye.items import BirdseyeItem


class ValleysurgSpider(scrapy.Spider):
    vendors = ''
    name = "valley"
    allowed_domains = ["valleysurg.com"]
    start_urls = []

    pagination_url = 'http://www.valleysurg.com/products?limit=100&page=%s'
    pag_max_count = 12

    def __init__(self, **kwargs):
        super(ValleysurgSpider, self).__init__(**kwargs)
        self.init_page_urls()

    def init_page_urls(self):
        for page_num in range(1, self.pag_max_count):
            url = self.pagination_url % page_num
            self.start_urls = self.start_urls + [url]

    def parse(self, response):
        urls = response.css('div.image a::attr(href)').extract()
        for num in range(len(urls)):
            url = urls[num]
            item = BirdseyeItem()
            item['url'] = url.strip()
            item['vendor'] = 'http://www.valleysurg.com/'
            request = scrapy.Request(item['url'], callback=self.parse_event, meta={'item': item})
            yield request

    def parse_event(self, response):
        sel = response.css('html')
        item = response.meta['item']
        product_name = sel.css('div.breadcrumb a:last-child::text').extract()[0]
        item['product_name'] = product_name
        item['oem'] = product_name.split(':')[1].strip()
        item['product_url'] = response.request.url

        description = sel.css('div#tab-description').extract()[0]
        item['description'] = description

        price = sel.css('div.price::text').extract()[0]
        item['price'] = price.split(':')[0].strip()
        item['manufacturer'] = 'VALLEY SURGICAL'

        try:
            stock = sel.css('div.description::text').extract()
            item['stock_quantity'] = stock[len(stock) - 1]
        except Exception as e:
            item['stock_quantity'] = 'out of stock'
        pass

        yield item

    def get_dict(self, path):
        with open(path, 'r') as f:
            data = json.load(f)
        return data