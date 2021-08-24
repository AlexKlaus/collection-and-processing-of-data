import requests
from bs4 import BeautifulSoup as bs
from pprint import pprint
import re
from decimal import Decimal
import pandas as pd


def create_soup(url, params, target):
    """
        Создает суп из блока вакансии
    """
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/91.0.4472.164 Safari/537.36'}
    response = requests.get(url, params=params, headers=headers)
    soup = bs(response.text, 'html.parser')
    return soup.find_all(*target)


def get_hh_vacancies(page_number):
    """
        Получить вакансии с одной страницы
    """
    hh_url = 'https://www.hh.ru/'
    hh_soup = create_soup(hh_url + 'search/vacancy',
                          {'fromSearchLine': 'true',
                           'st': 'searchVacancy',
                           'text': profession,
                           'customDomain': '1',
                           'page': page_number},
                          ('div', {'class': 'vacancy-serp-item'}))
    list_of_vacancies = []
    for vacancy in hh_soup:
        vacancy_data = {}

        vacancy_title = vacancy.find('a', {'class': 'bloko-link'})
        salary_info = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
        vacancy_link = vacancy.find('a', {'class': 'bloko-link'})
        try:
            salary_info = salary_info.text
            currency = re.search(r'\S+$', salary_info)[0]
            salaries = [Decimal(''.join(x.split('\u202f'))).quantize(Decimal('1.'))
                        for x in re.findall(r'\d+\s+\d+', salary_info)] or \
                       [Decimal(re.findall(r'\d+', salary_info)[0]).quantize(Decimal('1.'))]
            min_salary = salaries[0]
            if len(salaries) > 1:
                max_salary = salaries[1]
            else:
                max_salary = None
        except AttributeError:
            currency = None
            min_salary = None
            max_salary = None

        vacancy_data['vacancy_title'] = vacancy_title.text
        vacancy_data['min_salary'] = min_salary
        vacancy_data['max_salary'] = max_salary
        vacancy_data['currency'] = currency
        vacancy_data['vacancy_link'] = vacancy_link.get('href')
        vacancy_data['vacancy_site'] = hh_url
        list_of_vacancies.append(vacancy_data)
    return list_of_vacancies


def get_sjob_vacancies(page):
    """
        Получить вакансии с одной страницы
    """
    sjob_url = 'https://russia.superjob.ru/'
    sj_soup = create_soup(sjob_url + 'vacancy/search',
                          {'keywords': profession,
                           'page': page},
                          ('div', {'class': 'f-test-vacancy-item'}))
    list_of_vacancies = []
    for vacancy in sj_soup:
        vacancy_data = {}
        vacancy_title = vacancy.find('a', {'class': 'icMQ_'})
        salary_info = vacancy.findChild('span', {'f-test-text-company-item-salary'}).text
        vacancy_link = vacancy.find('a')
        if salary_info == 'По договорённости':
            currency = None
            min_salary = None
            max_salary = None
        else:
            currency = re.search(r'\S+\.', salary_info)[0]
            salaries = [Decimal(''.join(x.split('\xa0'))).quantize(Decimal('1.'))
                        for x in re.findall(r'\d+\s+\d+', salary_info)] or \
                       [Decimal(re.findall(r'\d+', salary_info)[0]).quantize(Decimal('1.'))]
            min_salary = salaries[0]
            if len(salaries) > 1:
                max_salary = salaries[1]
            else:
                max_salary = None

        vacancy_data['vacancy_title'] = vacancy_title.text
        vacancy_data['min_salary'] = min_salary
        vacancy_data['max_salary'] = max_salary
        vacancy_data['currency'] = currency
        vacancy_data['vacancy_link'] = sjob_url[:-1] + vacancy_link.get('href')
        vacancy_data['vacancy_site'] = sjob_url
        list_of_vacancies.append(vacancy_data)
    return list_of_vacancies


def get_all_vacancies(quantity_pages, from_one_page_function):
    """
        Получить вакансии с указаного количества страниц
    """
    all_vacancies_list = []
    for n in range(quantity_pages):
        vacancies_from_page = from_one_page_function(n)
        if not vacancies_from_page:
            break
        all_vacancies_list += vacancies_from_page
    return all_vacancies_list


profession = input('Введите желаемую должность: ')
quantity_of_pages = int(input('Количесто страниц для парсинга: '))

hh_all_vacancies = pd.DataFrame(get_all_vacancies(quantity_of_pages, get_hh_vacancies))
sjob_all_vacancies = pd.DataFrame(get_all_vacancies(quantity_of_pages, get_sjob_vacancies))
all_vacancies = hh_all_vacancies.append(sjob_all_vacancies, ignore_index=True)

pprint(all_vacancies)

with open('data.csv', 'w') as f:
    f.write(all_vacancies.to_csv())
