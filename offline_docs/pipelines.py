# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import hashlib
import six
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
    ASSETS_STORE = 'assets'

    FIELDS = {
        'css_raw_urls':'css_files',
        'js_raw_urls':'js_files',
        'image_raw_urls':'images',
    }

    @classmethod
    def from_crawler(cls, crawler):
        pipe = cls()
        pipe.DOCS_STORE = crawler.settings['DOCS_STORE']
        pipe.ASSETS_STORE = crawler.settings['ASSETS_STORE']
        return pipe

    def process_item(self,item,spider):
        path = os.path.normpath(urlparse(item['url']).path[1:])
        filename = os.path.join(self.DOCS_STORE,path)
        dirname = os.path.dirname(filename)
        if not os.path.isdir(dirname):
            os.makedirs(dirname,0o755)

        deep = len(path.split('/'))-1
        item = self.process_assets(item,'%s%s/' % ('../'*deep,os.path.basename(self.ASSETS_STORE)))
        with open(filename,'wb') as f:
            f.write(item['body'].encode('utf-8'))

        return item

    #Rude way
    def process_assets(self,item,basepath):
        for k,v in self.FIELDS.items():
            raw_urls = item.get(k)
            save_files = item.get(v)
            if not raw_urls or not save_files or not isinstance(save_files,list):
                continue
            i = 0
            for sf in save_files:
                if len(raw_urls) <=i:
                    break
                if type(item['body']) is not unicode:
                    item['body'] = item['body'].decode('utf-8')
                item['body'] =item['body'].replace(raw_urls[i],basepath+sf.get('path',''))
                i=i+1
        return item

