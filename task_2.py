from pprint import pprint
from task_1 import VACANCIES


# минимальная зарплата есть в любом случае, я не понимаю зачем сравнивать оба поля
SALARY = int(input('Введите желаемую зарплату: '))
for vac in VACANCIES.find({'min_salary': {'$gt': SALARY}}):
    max_sal = vac.get('max_salary')
    if not max_sal or max_sal > SALARY:
        pprint(vac)
