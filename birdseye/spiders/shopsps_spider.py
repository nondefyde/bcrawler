import scrapy
from birdseye.items import BirdseyeItem


class ShopspsSpider(scrapy.Spider):
    name = "sps"
    allowed_domains = ["shopsps.com"]
    start_urls = ['http://shopsps.com/collections/all']

    pagination_url = 'http://shopsps.com/collections/all?page=%s'
    pag_max_count = 279

    def __init__(self, **kwargs):
        super(ShopspsSpider, self).__init__(**kwargs)
        self.init_page_urls()

    def init_page_urls(self):
        for page_num in range(1, self.pag_max_count):
            url = self.pagination_url % page_num
            self.start_urls = self.start_urls + [url]
            break

    def parse(self, response):
        urls = response.css('div.details h3 a::attr(href)').extract()
        for num in range(len(urls)):
            url = urls[num]
            item = BirdseyeItem()
            item['url'] = 'http://shop.anewmed.com' + url.strip()
            item['vendor'] = 'http://shopsps.com'
            # request = scrapy.Request(item['url'], callback=self.parse_event, meta={'item': item})
            yield item
            break

    def parse_event(self, response):
        sel = response.css('body')
        item = response.meta['item']

        item['product_name'] = sel.css('div h1.title::text').extract()[0]
        oem = sel.css('div h3#sku::title').extract()[1]
        item['oem'] = (oem.split(':')[0]).strip()
        item['manufacturer'] = ''
        item['description'] = ''
        item['product_url'] = response.request.url

        item['stock_quantity'] = sel.css('div.variant-inventory p span::text').extract()[0]

        try:
            item['price'] = sel.css('div.purchase h2.price::text').extract()[0]
        except Exception as e:
            item['price'] = '0'
        pass

        yield item

