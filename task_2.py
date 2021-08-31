"""Сложить собранные данные в БД"""
import hashlib
import json
import pymongo.errors
from pymongo import MongoClient
from task_1 import parse_technology_news, ITEMS

CLIENT = MongoClient('127.0.0.1', 27017)
DB = CLIENT['yandex_news']
YANDEX_NEWS = DB.yandex_news


def add_to_db(news_list):
    """Добавляет новости в БД"""
    for news in news_list:
        try:
            YANDEX_NEWS.insert_one(
                {'_id': hashlib.sha256(
                    json.dumps(news.get('news_title') + news.get('source_name')
                               ).encode()).hexdigest(),
                 **news})
        except pymongo.errors.DuplicateKeyError:
            continue
    print("Новости добавлены в базу данных.")


NEWS = parse_technology_news(ITEMS)
add_to_db(NEWS)
