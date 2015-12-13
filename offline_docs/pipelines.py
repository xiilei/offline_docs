# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import hashlib
from six.moves.urllib.parse import urlparse

from bs4 import BeautifulSoup

from scrapy.http import Request
from scrapy.selector import Selector
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

    SEL_FIELDS = {
        'link':({'type':'text/css'},'href','css_raw_urls','css_files'),
        'script':({'type':'text/javascript'},'src','js_raw_urls','js_files'),
        'img':(None,'src','image_raw_urls','images'),
    }

    @classmethod
    def from_crawler(cls, crawler):
        pipe = cls()
        pipe.DOCS_STORE = crawler.settings['DOCS_STORE']
        pipe.ASSETS_STORE = crawler.settings['ASSETS_STORE']
        return pipe

    def process_item(self,item,spider):
        path = self.get_html_filepath(urlparse(item['url']).path)
        filename = os.path.join(self.DOCS_STORE,path)
        dirname = os.path.dirname(filename)
        if not os.path.isdir(dirname):
            os.makedirs(dirname,0o755)

        deep = len(path.split('/'))-1
        item = self.process_path(item,'%s%s/' % ('../'*deep,os.path.basename(self.ASSETS_STORE)))
        with open(filename,'wb') as f:
            f.write(item['body'].encode('utf-8'))

        return item

    def get_html_filepath(self,path):
        path = os.path.normpath(path)
        if path.endswith('/'):
            path = path+'index.html'
        elif path.endswith('.html') or path.endswith('.htm'):
            pass
        else:
            path = path+'.html'
        if path.startswith('/'):
            path = path[1:]
        return path

    def pre_urls_dict(self,raw_urls,save_path):
        if len(raw_urls)!=len(save_path):
            raise TypeError('raw_urls and save_path length not equal')
        urls_dict = dict()
        i = 0
        for url in raw_urls:
            urls_dict[url] = save_path[i]['path']
            i=i+1
        return urls_dict

    def process_path(self,item,basepath,urlpath):
        soup = BeautifulSoup(item['body'],'lxml')
        for find_tag,v in self.SEL_FIELDS.items():
            find_attr,attr,raw_field,save_field = v
            urls_dict = self.pre_urls_dict(item.get(raw_field),item.get(save_field))
            for tag in soup.find_all(find_tag,find_attr):
                value = urls_dict.get(tag[attr])
                if not value:
                    continue
                tag[attr] = basepath+value
        for a_tag in soup.find_all('a'):
            if a_tag['href']:
                a_tag['href'] = self.get_html_filepath(a_tag['href'])
        item['body'] = soup.prettify()
        return item



