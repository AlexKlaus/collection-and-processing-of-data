from pprint import pprint
from task_1 import VACANCIES


SALARY = int(input('Введите желаемую зарплату: '))
for vac in VACANCIES.find({'$or': [
        {'min_salary': {'$gt': SALARY}},
        {'max_salary': {'$gt': SALARY}}
]}):
    pprint(vac)
