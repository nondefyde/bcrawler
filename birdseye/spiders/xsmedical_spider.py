import scrapy
from birdseye.items import BirdseyeItem


class EventEyeSpider(scrapy.Spider):
    google_maps = ''
    month = []

    name = "xsmedical"
    allowed_domains = ["xsmedical.com"]
    # start_urls = ['http://www.eventseye.com/fairs/Upcoming_Trade_Shows.html']
    start_urls = ['http://www.xsmedical.com']

    def parse(self, response):

        urls = response.css('table.productTable td.titleRow a::attr(href)').extract()
        titles = response.css('table.productTable td.titleRow a::text').extract()
        for num in range(len(urls)):
            url = urls[num]
            title = titles[num]
            item = BirdseyeItem()
            item['url'] = 'http://shop.anewmed.com' + url.strip()
            item['name'] = title.strip()
            request = scrapy.Request(item['url'], callback=self.parse_event, meta={'item': item})
            yield request
            break
            # yield item

    def parse_event(self, response):
        sel = response.css('html')
        item = response.meta['item']

        item['stock_quantity'] = sel.css('table tr span.prodAvailQty::text').extract()
        item['price'] = sel.css('table tr span.listPrice::text').extract()

        print item