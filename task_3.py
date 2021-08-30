import hashlib
from task_1 import VACANCIES, add_to_db


def only_new_by_hash(vacancy):
    """
    Добавляет только новые или обновленные вакансии
    :param vacancy:Данные вакансии
    """
    id_hash = hashlib.sha1(str(vacancy).encode())
    hashes_in_db = [h['_id'] for h in VACANCIES.find({})]
    if id_hash.hexdigest() not in hashes_in_db:
        add_to_db(vacancy)


def only_new_by_address(vacancy):
    """
    Добавляет только новые по ссылке
    :param vacancy:Данные вакансии
    """
    link = vacancy['vacancy_link']
    all_links = [lnk['vacancy_link'] for lnk in VACANCIES.find({})]
    if link not in all_links:
        add_to_db(vacancy)
