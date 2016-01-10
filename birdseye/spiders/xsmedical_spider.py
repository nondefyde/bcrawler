import json
import scrapy
from birdseye.items import BirdseyeItem


class XsmedicalSpider(scrapy.Spider):
    name = "xmedical"
    allowed_domains = ["xsmedical.com"]
    start_urls = []

    def __init__(self, **kwargs):
        super(XsmedicalSpider, self).__init__(**kwargs)
        urls = self.get_dict('assets//xsmedical_start_urls.json')
        for url in urls:
            self.start_urls = self.start_urls + [url['url']]

    def parse(self, response):
        urls = response.css('table div a.productnamecolor::attr(href)').extract()
        for num in range(len(urls)):
            url = urls[num]
            item = BirdseyeItem()
            item['url'] = url.strip()
            item['vendor'] = 'http://www.xsmedical.com'
            request = scrapy.Request(item['url'], callback=self.parse_event, meta={'item': item})
            yield request

    def parse_event(self, response):
        sel = response.css('html')
        item = response.meta['item']

        item['product_name'] = sel.css('font.colors_productname span::text').extract()[0]
        item['price'] = sel.css('div.product_productprice b span::text').extract()[0]
        item['product_url'] = response.request.url
        description = sel.css('span#product_description::text').extract()
        desc = ''.join(description)
        item['description'] = desc
        item['manufacturer'] = sel.css('table td meta[itemprop="manufacturer"]::attr(content)').extract()
        item['oem'] = sel.css('span.product_code::text').extract()[0]

        try:
            item['stock_quantity'] = sel.css('table input.v65-productdetail-cartqty::attr(value)').extract()[0]
        except Exception as e:
            item['stock_quantity'] = '0'
        pass

        yield item

    def get_dict(self, path):
        with open(path, 'r') as f:
            data = json.load(f)
        return data