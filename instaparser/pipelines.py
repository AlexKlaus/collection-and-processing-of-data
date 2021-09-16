# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient



class InstaparserPipeline:
    def __init__(self):
        client = MongoClient('127.0.0.1', 27017)
        self.mongo_base = client.insta


    def process_item(self, item, spider):
        collection = self.mongo_base[f"{item['parsed_user']}'s followers"]
        del item['parsed_user']
        collection.insert_one(item)

        return item
