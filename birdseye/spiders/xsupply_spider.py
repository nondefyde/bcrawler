import json
import scrapy
from birdseye.items import BirdseyeItem


class XsupplySpider(scrapy.Spider):
    name = "xsupply"
    allowed_domains = ["xs-supply.com"]
    start_urls = []

    def __init__(self, **kwargs):
        super(XsupplySpider, self).__init__(**kwargs)
        urls = self.get_dict('assets//xsupply_start_urls.json')
        for url in urls:
            self.start_urls = self.start_urls + [url['url']]

    def parse(self, response):
        urls = response.css('div.item-image a::attr(href)').extract()
        title = response.css('h1')
        prices = response.css('div.item-price::text').extract()
        quantities = response.css('p#inventory-message::text').extract()
        oems = response.css('div.item-details h5 a::text').extract()
        print title
        for num in range(len(urls)):
            url = urls[num]
            item = BirdseyeItem()
            item['url'] = url.strip()
            item['vendor'] = 'http://www.xs-supply.com'
            title = response.request.url
            try:
                title = title[title.rindex('=') + 1:]
            except Exception as e:
                title = title[title.rindex('/') + 1:title.rindex('.')]
            pass

            item['product_name'] = title
            item['price'] = (prices[num]).strip()
            item['stock_quantity'] = quantities[num]
            item['product_url'] = url.strip()
            item['oem'] = oems[num]
            item['manufacturer'] = 'XS-SUPPLY'
            item['description'] = ''
            yield item

        paging = response.css('span.current + a::attr(href)').extract()
        if len(paging) > 0:
            next_page = paging[0].strip()
            request = scrapy.Request(next_page, callback=self.parse)
            yield request

    def get_dict(self, path):
        with open(path, 'r') as f:
            data = json.load(f)
        return data