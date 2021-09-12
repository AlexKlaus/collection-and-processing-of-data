import scrapy
from scrapy.http import HtmlResponse
from leruaparser.items import LeruaparserItem
from scrapy.loader import ItemLoader


class LeroyruSpider(scrapy.Spider):
    name = 'leroyru'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, query, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [f'https://leroymerlin.ru/catalogue/{query}/']

    def parse(self, response: HtmlResponse):
        """Получаем ссылки на объекты и ссылку на след. страницу"""
        links = response.xpath("//a[@data-qa='product-name']")
        next_page = response.xpath("//a[contains(@aria-label, 'Следующая')]/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        for link in links:
            yield response.follow(link, callback=self.parse_item)

    def parse_item(self, response: HtmlResponse):
        loader = ItemLoader(item=LeruaparserItem(), response=response)
        loader.add_xpath('name', "//h1/text()")
        loader.add_xpath('photos', "//img[@alt='product image']/@src")
        parameters = dict(zip(response.xpath("//dt/text()").getall(),
                              response.xpath("//dd/text()").getall()))
        loader.add_value('parameters', parameters)
        loader.add_value('url', response.url)
        loader.add_xpath('price', "//span[@slot='price']/text()")
        yield loader.load_item()
