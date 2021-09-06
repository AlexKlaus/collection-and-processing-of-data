import json
import pymongo.errors
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from pymongo import MongoClient

CLIENT = MongoClient('127.0.0.1', 27017)
DB = CLIENT['mvideo']
mvideo = DB.mvideo

chrome_options = Options()
chrome_options.add_argument('start-maximized')

driver = webdriver.Chrome(executable_path='./chromedriver', options=chrome_options)

driver.get('https://www.mvideo.ru/')

new_items_section = driver.find_element_by_xpath("//h2[contains(text(), 'Новинки')]")
actions = ActionChains(driver)
actions.move_to_element(new_items_section)
actions.key_down(Keys.PAGE_DOWN).key_up(Keys.PAGE_DOWN)
actions.perform()
arrow = driver.find_element_by_xpath(
        "//h2[contains(text(), 'Новинки')]/../../..//a[contains(@class, 'next-btn')]")

while True:
    if 'disabled' in arrow.get_attribute('class'):
        break
    arrow.click()

items = driver.find_elements_by_xpath(
    "//h2[contains(text(), 'Новинки')]/../../.."
    "//a[@data-product-info and contains(@class, 'title__link')]")

for i in items:
    item = json.loads(
        i.get_attribute('data-product-info').replace('\n', '').replace('\t\t\t\t\t', ''))
    try:
        mvideo.insert_one(
            {'_id': item['productId'],
             **item})
    except pymongo.errors.DuplicateKeyError:
        continue
