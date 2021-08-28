import re
import hashlib
import requests
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient
import pymongo.errors


CLIENT = MongoClient('127.0.0.1', 27017)
DB = CLIENT['vacancies']
VACANCIES = DB.vacancies


def create_soup(url, params, target):
    """
        Создает суп из блока вакансии
    """
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                             '(KHTML, like Gecko) '
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
                           'text': PROFESSION,
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
            salaries = [float(''.join(x.split('\u202f')))
                        for x in re.findall(r'\d+\s+\d+', salary_info)] or \
                       [float(re.findall(r'\d+', salary_info)[0])]
            min_salary = salaries[0]
            if len(salaries) > 1:
                max_salary = salaries[1]
            elif re.search(r'^\S+', salary_info)[0] == 'до':
                min_salary = None
                max_salary = salaries[0]
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
        try:
            add_to_db(vacancy_data)
        except pymongo.errors.DuplicateKeyError:
            continue
    return list_of_vacancies


def get_sjob_vacancies(page):
    """
        Получить вакансии с одной страницы
    """
    sjob_url = 'https://russia.superjob.ru/'
    sj_soup = create_soup(sjob_url + 'vacancy/search',
                          {'keywords': PROFESSION,
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
            salaries = [float(''.join(x.split('\xa0')))
                        for x in re.findall(r'\d+\s+\d+', salary_info)] or \
                       [float(re.findall(r'\d+', salary_info)[0])]
            min_salary = salaries[0]
            if len(salaries) > 1:
                max_salary = salaries[1]
            elif re.search(r'^\S+', salary_info)[0] == 'до':
                min_salary = None
                max_salary = salaries[0]
            else:
                max_salary = None

        vacancy_data['vacancy_title'] = vacancy_title.text
        vacancy_data['min_salary'] = min_salary
        vacancy_data['max_salary'] = max_salary
        vacancy_data['currency'] = currency
        vacancy_data['vacancy_link'] = sjob_url[:-1] + vacancy_link.get('href')
        vacancy_data['vacancy_site'] = sjob_url
        list_of_vacancies.append(vacancy_data)
        try:
            add_to_db(vacancy_data)
        except pymongo.errors.DuplicateKeyError:
            continue
    return list_of_vacancies


def get_all_vacancies(quantity_pages, from_one_page_function):
    """
        Получить вакансии с указаного количества страниц
    """
    all_vacancies_list = []
    for _ in range(quantity_pages):
        vacancies_from_page = from_one_page_function(_)
        if not vacancies_from_page:
            break
        all_vacancies_list += vacancies_from_page
    return all_vacancies_list


def add_to_db(vacancy):
    """
    Добавляет вакансию в баз данных
    :param vacancy:Данные вакансии
    """
    id_hash = hashlib.sha1(str(vacancy).encode())
    VACANCIES.insert_one({'_id': id_hash.hexdigest(), **vacancy})


if __name__ == '__main__':
    PROFESSION = input('Введите желаемую должность: ')
    QUANTITY_OF_PAGES = int(input('Количесто страниц для парсинга: '))

    get_all_vacancies(QUANTITY_OF_PAGES, get_hh_vacancies)
    get_all_vacancies(QUANTITY_OF_PAGES, get_sjob_vacancies)
