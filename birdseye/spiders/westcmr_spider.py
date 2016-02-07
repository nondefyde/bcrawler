import json
import scrapy
from birdseye.items import BirdseyeItem


class ShopspsSpider(scrapy.Spider):
    vendors = ''
    name = "west"
    allowed_domains = ["westcmr.com"]
    start_urls = [
        # 'http://www.westcmr.com/covidien'
        # 'http://www.westcmr.com/anspach'
    ]

    def __init__(self, **kwargs):
        super(ShopspsSpider, self).__init__(**kwargs)
        self.vendors = self.get_dict('assets//westcmr_vendors.json')
        for path in self.vendors:
            url = path['url']
            self.start_urls = self.start_urls + [url]

    def parse(self, response):
        last_page_no = response.css('input#LastPageNumber::attr(value)').extract()
        print last_page_no
        if len(last_page_no) > 0:
            url = response.request.url + "?page="+last_page_no[0]
        else:
            url = response.request.url

        request = scrapy.Request(url, callback=self.full_page_parse)
        yield request

    def full_page_parse(self, response):

        print response.request.url

        urls = response.css('ul.unstyled li.product-title a::attr(href)').extract()
        for num in range(len(urls)):
            url = urls[num]
            item = BirdseyeItem()
            item['url'] = 'http://www.westcmr.com' + url.strip()
            item['vendor'] = 'http://www.westcmr.com'
            request = scrapy.Request(item['url'], callback=self.parse_event, meta={'item': item})
            yield request
        #
        # view_more_url = response.css('a.btn-view-more::attr(href)').extract()
        # if len(view_more_url) > 0:
        #     more_page_url = 'http://www.westcmr.com' + view_more_url[0]
        #     yield scrapy.Request(more_page_url, callback=self.parse)
        #
        # print response.request.url

    def parse_event(self, response):
        sel = response.css('body')
        item = response.meta['item']

        item['product_name'] = sel.css('div.row-fluid h1::text').extract()[0]
        oem = sel.css('div.row-fluid p::text').extract()[0]
        item['oem'] = oem.split(':')[1].strip()

        item['description'] = ''
        item['product_url'] = response.request.url
        item['stock_quantity'] = sel.css('div.boxshad table td::text').extract()[1].strip()
        try:
            item['price'] = (sel.css('strong.price::text').extract()[0]).split(' ')[1].strip()
        except Exception as e:
            item['price'] = 'Call For Price'
        pass

        item['manufacturer'] = ''
        for vendor in self.vendors:
            manufacturer = vendor['manufacturer']
            partial = item['product_name']
            partial = partial.split('-')
            partial = ' ' .join(partial)
            search = manufacturer in partial
            if search:
                item['manufacturer'] = manufacturer

        yield item

    def get_dict(self, path):
        with open(path, 'r') as f:
            data = json.load(f)
        return data