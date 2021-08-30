from pprint import pprint
from task_1 import VACANCIES


def get_good_job(salary):
    """
    Возвращает вакансии у которых минимальная зарплата выше указаной,
    если указаны и минимальная и максимальная, но минимальная ниже, то эта вакансия не подходит,
    если минимальная не указана, но з.п. "до" выше запрашиваемой, то эта вакансия попадет в вывод.
    :param salary: сумма зарплаты
    """
    for vac in VACANCIES.find({'$or': [
            {'min_salary': {'$gt': salary}},
            {'max_salary': {'$gt': salary}}
    ]}):
        if vac.get('min_salary') and vac.get('min_salary') < salary:
            continue
        pprint(vac)


get_good_job(int(input('Введите желаемую зарплату: ')))
