import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=Python&geo%5Bt%5D%5B0%5D=4',
                  'https://www.superjob.ru/vacancy/search/?keywords=Python&geo%5Br%5D%5B0%5D=2']


    def parse(self, response: HtmlResponse):
        links = response.xpath("//div[@class='f-test-search-result-item']//a[contains(@href, 'vakansii')]/@href").getall()
        next_page = response.xpath("//a[contains(@class, 'f-test-button-dalshe')]/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        for link in links:
            yield response.follow(link, callback=self.parse_vacancy)


    def parse_vacancy(self, response: HtmlResponse):
        vac_name = response.xpath("//h1/text()").get()
        vac_salary = response.xpath("//div[contains(@class, 'f-test-address')]"
                                    "/following-sibling::span").get()
        vac_url = response.url
        yield JobparserItem(name=vac_name, salary=vac_salary, url=vac_url)
