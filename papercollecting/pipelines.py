# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from papercollecting.items import *
class PapercollectingPipeline(object):
    def process_item(self, item, spider):
        return item


class MongoDBPipeline(object):

    collection_name = 'articles'

    def __init__(self, mongodb_host = '127.0.0.1', mongodb_db = 'papers'):
        self.mongo_uri = mongodb_host
        self.mongo_db = mongodb_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(

        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient()
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        # if self.db[self.collection_name].count()>70000:
        #     raise CloseSpider("out")
        if isinstance(item, PaperItem):
            paper = self.db['papers'].find_one({'arxiv_id': item['arxiv_id']})
            item['category'] = [item['category']]
            if paper:
                tmp = item['category']
                categories = paper['category']
                categories.extend(tmp)
                item['category'] = categories
            self.db['papers'].update({'arxiv_id': item['arxiv_id']},  dict(item), True)
        elif isinstance(item, ACMProceeding):
            self.db['acm_proceedings'].insert_one(dict(item))
