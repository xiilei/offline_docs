# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import hashlib

from scrapy.http import Request
from scrapy.pipelines.files import FilesPipeline
from scrapy.exceptions import NotConfigured

class DocPipeline(object):

    def process_item(self,item,spider):
        return item

class AssetsPipeline(FilesPipeline):

    @classmethod
    def from_settings(cls, settings):
        s3store = cls.STORE_SCHEMES['s3']
        s3store.AWS_ACCESS_KEY_ID = settings['AWS_ACCESS_KEY_ID']
        s3store.AWS_SECRET_ACCESS_KEY = settings['AWS_SECRET_ACCESS_KEY']
        store_uri = settings['ASSETS_STORE'] 
        return cls(store_uri)

    def file_path(self, request, response=None, info=None):
        media_guid = hashlib.sha1(request.url.encode('utf-8')).hexdigest()
        filename = '%s/%s.%s' % (self.get_type(),media_guid, self.get_type())
        return filename

    def get_media_requests(self, item, info):
        return [Request(x) for x in item.get(self.ASSETS_URLS_FIELD, {})]

    def item_completed(self, results, item, info):
        if isinstance(item, dict) or self.ASSETS_RESULT_FIELD in item.fields:
            item[self.ASSETS_RESULT_FIELD] = [x for ok, x in results if ok]
        return item

    ASSETS_URLS_FIELD = 'css_urls'
    ASSETS_RESULT_FIELD = 'css_urls'

    def get_type():
        return 'css'

class CssPipeline(AssetsPipeline):

    ASSETS_URLS_FIELD = 'css_urls'
    ASSETS_RESULT_FIELD = 'css_urls'

    def get_type():
        return 'css'

class JsPipeline(AssetsPipeline):

    ASSETS_URLS_FIELD = 'js_urls'
    ASSETS_RESULT_FIELD = 'js_files'

    def get_type():
        return 'js'

    
