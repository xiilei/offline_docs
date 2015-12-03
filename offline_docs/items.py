# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DocItem(scrapy.Item):
    image_urls = scrapy.Field()
    image_raw_urls = scrapy.Field()
    images = scrapy.Field()

    js_urls = scrapy.Field()
    js_raw_urls = scrapy.Field()
    js_files = scrapy.Field()

    css_urls = scrapy.Field()
    css_raw_urls = scrapy.Field()
    css_files = scrapy.Field()
    
    body = scrapy.Field()
    url = scrapy.Field()

        
