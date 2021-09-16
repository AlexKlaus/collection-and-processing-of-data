# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
import re


class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.vacancy0209


    def process_item(self, item, spider):
        if spider.name == 'hhru':
            min_salary, max_salary, currency = self.process_salary_hh(item['salary'])
            item['site'] = 'https://hh.ru/'
        else:
            min_salary, max_salary, currency = self.process_salary_sjob(item['salary'])
            item['site'] = 'https://www.superjob.ru/'
        item['salary'] = {'min_salary': min_salary,
                          'max_salary': max_salary,
                          'currency': currency}
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item


    def process_salary_hh(self, salary):
        """Обработка зарплаты у вакансии"""
        min_salary = None
        max_salary = None
        cur = None
        if salary or salary != 'з/п не указана':
            cur = salary.split(' ')[-1]
            salary_sum = [float(x.replace('\xa0', ''))
                          for x in
                          re.findall(r'\d+\s+\d+', salary)]
            if len(salary_sum) == 2:
                min_salary = salary_sum[0]
                max_salary = salary_sum[1]
            elif 'до' in salary:
                max_salary = salary_sum[0]
            else:
                min_salary = salary_sum[0]
        return min_salary, max_salary, cur


    def process_salary_sjob(self, salary):
        """Обработка зарплаты у вакансии"""
        min_salary = None
        max_salary = None
        cur = None
        salary = re.sub(r'\<[^>]*\>', '', salary)
        if salary != 'По договорённости':
            cur = salary.split('\xa0')[-1].replace('/месяц', '').replace('/день', '')
            salary_sum = [float(x.replace('\xa0', ''))
                          for x in
                          re.findall(r'\d+\s+\d+', salary)]
            if len(salary_sum) == 2:
                min_salary = salary_sum[0]
                max_salary = salary_sum[1]
            elif 'до' in salary:
                max_salary = salary_sum[0]
            else:
                min_salary = salary_sum[0]
        return min_salary, max_salary, cur
