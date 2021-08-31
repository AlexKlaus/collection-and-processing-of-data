"""Написать приложение, которое собирает основные новости
с сайта на выбор news.mail.ru, lenta.ru, yandex-новости.
Для парсинга использовать XPath. Структура данных должна содержать:
название источника;
наименование новости;
ссылку на новость;
дата публикации."""
from pprint import pprint
from datetime import datetime
from lxml import html
import requests

HEADER = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                        '(KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36'}
RESPONSE = requests.get('https://yandex.ru/news/', headers=HEADER)
DOM = html.fromstring(RESPONSE.text)
ITEMS = DOM.xpath(
    "//a[text()='Технологии']/../../../following-sibling::div[1]//article")


def parse_technology_news(items):
    """
        Функция возвращает новости из раздела 'Технологии'
    """
    item_list = []
    for item in items:
        items_data = {}
        source_name = item.xpath(".//a/@aria-label")
        news_title = item.xpath(".//h2/text()")
        link = item.xpath(".//a[@class='mg-card__link']/@href")
        time = item.xpath(".//span[@class='mg-card-source__time']/text()")

        items_data['news_title'] = news_title[0].replace('\xa0', ' ')
        items_data['source_name'] = source_name[0].replace('Источник: ', '')
        items_data['link'] = link[0]
        items_data['date'] = f'{datetime.date(datetime.today())} {time[0]}'

        item_list.append(items_data)
    return item_list


if __name__ == '__main__':
    pprint(parse_technology_news(ITEMS))
