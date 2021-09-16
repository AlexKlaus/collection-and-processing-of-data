# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    followers_or_followings = scrapy.Field()
    parsed_user = scrapy.Field()
    name = scrapy.Field()
    id = scrapy.Field()
    picture = scrapy.Field()






