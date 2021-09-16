from pymongo import MongoClient
from pprint import pprint

client = MongoClient('127.0.0.1', 27017)
mongo_base = client.insta
user = 'rollomaticsa'
# 4) Написать запрос к базе, который вернет список подписчиков только указанного пользователя
for user in mongo_base[user].find({'followers_or_followings': 'followers'}):
    pprint(user)

# 5) Написать запрос к базе, который вернет список профилей, на кого подписан указанный пользователь
for user in mongo_base[user].find({'followers_or_followings': 'followings'}):
    pprint(user)