# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst
import json


def process_parameters(params):
    """Обработка характеристик"""
    for key, value in params.items():
        clear_val = value.replace('\n', '').replace(' ', '')
        try:
            clear_val = json.loads(clear_val)
        except json.decoder.JSONDecodeError:
            pass
        params[key] = clear_val
    return params


def process_price(price):
    return json.loads(price.replace(' ', ''))


class LeruaparserItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    name = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
    parameters = scrapy.Field(input_processor=MapCompose(process_parameters), output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(process_price), output_processor=TakeFirst())
