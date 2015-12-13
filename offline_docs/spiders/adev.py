import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from offline_docs.items import DocItem

class AdevSpider(CrawlSpider):
    name = 'adev'
    # allowed_domains = ['google.com','googleapi.com','developer.android.com']
    # start_urls = ['http://developer.android.com/training/index.html']
    allowed_domains = ['localhost']
    start_urls = ['http://localhost/scrapytest/index.html']

    rules=(
        Rule(LinkExtractor(allow=('.*\.html$',),tags='a',attrs='href'),callback='parse_html'),
    )

    def parse_start_url(self,response):
        return self.parse_html(response)

    def parse_html(self,response):
        item = DocItem()
        item['body'] = response.body
        item['url'] = response.url

        urls_dict = {
            'image_urls':('//img/@src','image_raw_urls'),
            'css_urls':('//link[@type="text/css"]/@href','css_raw_urls'),
            'js_urls':('//script[@type="text/javascript"]/@src','js_raw_urls'),
        }

        for k,v in urls_dict.items():
            xpath,raw_field = v
            urls = [url for url in self._parse_urls(response,xpath=xpath)]
            if raw_field:
                item[raw_field] = urls
            item[k] = map(response.urljoin,urls)

        return item

    def _parse_urls(self,response,xpath):
        for src in response.xpath(xpath):
            yield src.extract()
