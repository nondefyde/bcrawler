import scrapy
from birdseye.items import BirdseyeItem


class AnewmedSpider(scrapy.Spider):
    name = "anewmed"
    allowed_domains = ["anewmed.com"]
    start_urls = [
        'http://shop.anewmed.com/In-Date-Devices_c16.htm',
        'http://shop.anewmed.com/Repackaged-Devices_c39.htm',
    ]

    def parse(self, response):
        cat_urls = response.css('ul li ul li a::attr(href)').extract()
        for num in range(len(cat_urls)):
            url = cat_urls[num]
            url = 'http://shop.anewmed.com' + url.strip()
            request = scrapy.Request(url, callback=self.parse_category)
            yield request

    def parse_category(self, response):
        urls = response.css('table.productTable td.titleRow a::attr(href)').extract()
        for num in range(len(urls)):
            url = urls[num]
            item = BirdseyeItem()
            item['url'] = 'http://shop.anewmed.com' + url.strip()
            item['vendor'] = 'http://shop.anewmed.com/'
            request = scrapy.Request(item['url'], callback=self.parse_event, meta={'item': item})
            yield request


    def parse_event(self, response):
        sel = response.css('body')
        item = response.meta['item']
        product_details = sel.css('div.product-details ul li::text').extract()

        item['product_name'] = sel.css('div.product-detail-header h2::text').extract()[0]
        item['price'] = sel.css('table tr span#listPrice::text').extract()[0]
        item['oem'] = (product_details[0]).strip().split(' ')[0]
        item['manufacturer'] = product_details[1]
        item['description'] = sel.css('div.product-description::text').extract()[0]
        item['product_url'] = response.request.url

        try:
            item['stock_quantity'] = sel.css('table tr span#prodAvailQty::text').extract()[0]
        except Exception as e:
            item['stock_quantity'] = 'out of stock'
        pass

        yield item