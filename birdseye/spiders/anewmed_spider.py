import scrapy
from birdseye.items import BirdseyeItem


class EventEyeSpider(scrapy.Spider):
    google_maps = ''
    month = []

    name = "anewmed"
    allowed_domains = ["anewmed.com"]
    start_urls = ['http://shop.anewmed.com/']

    def parse(self, response):

        urls = response.css('table.productTable td.titleRow a::attr(href)').extract()
        titles = response.css('table.productTable td.titleRow a::text').extract()
        for num in range(len(urls)):
            url = urls[num]
            title = titles[num]
            item = BirdseyeItem()
            item['url'] = 'http://shop.anewmed.com' + url.strip()
            item['product_name'] = title.strip()
            item['vendor'] = 'http://shop.anewmed.com/'
            request = scrapy.Request(item['url'], callback=self.parse_event, meta={'item': item})
            yield request

    def parse_event(self, response):
        sel = response.css('body')
        item = response.meta['item']
        product_details = sel.css('div.product-details ul li::text').extract()
        item['price'] = sel.css('table tr span#listPrice::text').extract()[0]

        try:
            item['stock_quantity'] = sel.css('table tr span#prodAvailQty::text').extract()[0]
        except Exception as e:
            item['stock_quantity'] = '0'
        pass

        item['oem'] = (product_details[0]).strip().split(' ')[0]
        item['manufacturer'] = product_details[1]
        item['description'] = sel.css('div.product-description::text').extract()[0]
        item['product_url'] = response.request.url

        yield item