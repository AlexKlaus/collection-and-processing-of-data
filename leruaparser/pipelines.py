# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
import hashlib
from pymongo import MongoClient


class LeruaparserPipeline:
    def __init__(self):
        client = MongoClient('127.0.0.1', 27017)
        self.mongo_base = client.leroy

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item


class LeruaPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    exit()

    def item_completed(self, results, item, info):
        item['photos'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        image_guid = hashlib.sha1(request.url.encode()).hexdigest()
        return f"full/{item['name'].replace(' ', '_').replace(',', '').replace('/', '_')}/{image_guid}.jpg"
