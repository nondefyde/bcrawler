import json
import scrapy
from birdseye.items import BirdseyeItem


class ShopspsSpider(scrapy.Spider):
    vendors = ''
    name = "sps"
    allowed_domains = ["shopsps.com"]
    start_urls = []

    pagination_url = 'http://shopsps.com/collections/all?page=%s'
    pag_max_count = 279

    def __init__(self, **kwargs):
        super(ShopspsSpider, self).__init__(**kwargs)
        self.vendors = self.get_dict('assets//shopsps_vendors.json')
        self.init_page_urls()

    def init_page_urls(self):
        for page_num in range(1, self.pag_max_count):
            url = self.pagination_url % page_num
            self.start_urls = self.start_urls + [url]
            # break

    def parse(self, response):
        urls = response.css('div.details h3 a::attr(href)').extract()
        for num in range(len(urls)):
            url = urls[num]
            item = BirdseyeItem()
            url = (url.strip())[url.strip().rindex('/'):]
            item['url'] = 'http://shopsps.com/products' + url.strip()
            item['vendor'] = 'http://shopsps.com'
            request = scrapy.Request(item['url'], callback=self.parse_event, meta={'item': item})
            yield request
            # print item

    def parse_event(self, response):
        sel = response.css('body')
        item = response.meta['item']

        item['product_name'] = sel.css('div h1.title::text').extract()[0]
        item['manufacturer'] = ''
        for vendor in self.vendors:
            manufacturer = vendor['manufacturer']
            search = manufacturer in item['product_name']
            if search:
                item['manufacturer'] = manufacturer

        oem = sel.css('div h3#sku::text').extract()[0]
        item['oem'] = oem.split(':')[1].strip()
        item['description'] = ''
        item['product_url'] = response.request.url
        item['stock_quantity'] = sel.css('div#variant-inventory p span::text').extract()[0]

        try:
            item['price'] = sel.css('div.purchase h2.price::text').extract()[0]
        except Exception as e:
            item['price'] = '0'
        pass

        yield item

    def get_dict(self, path):
        with open(path, 'r') as f:
            data = json.load(f)
        return data