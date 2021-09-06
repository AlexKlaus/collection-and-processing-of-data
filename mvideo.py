import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

chrome_options = Options()
chrome_options.add_argument('start-maximized')

driver = webdriver.Chrome(executable_path='./chromedriver', options=chrome_options)

driver.get('https://www.mvideo.ru/')

new_items_section = driver.find_element_by_xpath("//h2[contains(text(), 'Новинки')]")
actions = ActionChains(driver)
actions.move_to_element(new_items_section)
actions.key_down(Keys.PAGE_DOWN).key_up(Keys.PAGE_DOWN)
actions.perform()

items = driver.find_elements_by_xpath(
    "//h2[contains(text(), 'Новинки')]/../../..//a[@data-product-info and contains(@class, 'title__link')]")

data = []
actions = ActionChains(driver)
while True:
    for i in items:
        item = i.get_attribute('data-product-info').replace('\n', '').replace('\t\t\t\t\t', '')
        data.append(json.loads(item))
    arrow = driver.find_element_by_xpath(
        "//h2[contains(text(), 'Новинки')]/../../..//a[contains(@class, 'next-btn')]")
    if 'disabled' in arrow.get_attribute('class'):
        break
    actions.click(arrow)
    actions.perform()

print(len(data))
