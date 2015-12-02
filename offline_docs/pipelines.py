# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import hashlib
from six.moves.urllib.parse import urlparse

from scrapy.http import Request
from scrapy.pipelines.files import FilesPipeline
from scrapy.exceptions import NotConfigured


class AssetsPipeline(FilesPipeline):

    MEDIA_NAME = 'assets'

    @classmethod
    def from_settings(cls, settings):
        s3store = cls.STORE_SCHEMES['s3']
        s3store.AWS_ACCESS_KEY_ID = settings['AWS_ACCESS_KEY_ID']
        s3store.AWS_SECRET_ACCESS_KEY = settings['AWS_SECRET_ACCESS_KEY']
        store_uri = settings['ASSETS_STORE'] 
        return cls(store_uri)

    def file_path(self, request, response=None, info=None):
        media_guid = hashlib.sha1(request.url.encode('utf-8')).hexdigest()
        return '%s/%s.%s' % (self.ASSETS_TYPE, media_guid, self.ASSETS_TYPE)

    def get_media_requests(self, item, info):
        return [Request(x) for x in item.get(self.ASSETS_URLS_FIELD, {})]

    def item_completed(self, results, item, info):
        if isinstance(item, dict) or self.ASSETS_RESULT_FIELD in item.fields:
            item[self.ASSETS_RESULT_FIELD] = [x for ok, x in results if ok]
        return item

class CssPipeline(AssetsPipeline):

    MEDIA_NAME = 'style'
    ASSETS_TYPE = 'css'
    ASSETS_URLS_FIELD = 'css_urls'
    ASSETS_RESULT_FIELD = 'css_files'

class JsPipeline(AssetsPipeline):
    MEDIA_NAME = 'javascript'
    ASSETS_TYPE = 'js'
    ASSETS_URLS_FIELD = 'js_urls'
    ASSETS_RESULT_FIELD = 'js_files'

class DocPipeline(object):

    DOCS_STORE = './'

    FIELDS = {'css_raw_urls':'css_urls','js_raw_urls':'js_urls'}

    @classmethod
    def from_crawler(cls, crawler):
        pipe = cls()
        pipe.DOCS_STORE = crawler.settings['DOCS_STORE']
        return pipe

    def process_item(self,item,spider):
        filename = os.path.join(self.DOCS_STORE,urlparse(item['url']).path[1:])
        dirname = os.path.dirname(filename)
        if not os.path.isdir(dirname):
            os.makedirs(dirname,0o755)

        item = self.process_assets(item)
        with open(filename,'wb') as f:
            f.write(item['body'].encode('utf-8'))

        return item

    def process_assets(self,item):
        # for k,v in self.FIELDS.items():
        #     raw_urls = item.get(k)
        #     save_urls = item.get(k)
        #     if not raw_urls or not save_urls or not isinstance(raw_urls,list):
        #         continue
        #     i = 0
        #     for url in raw_urls:
        #         item['body'] = item['body'].replace()

        return item
    
