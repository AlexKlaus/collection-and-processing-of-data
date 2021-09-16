import scrapy
import re
import json
from scrapy.http import HtmlResponse
from urllib.parse import urlencode
from copy import deepcopy
from instaparser.items import InstaparserItem

class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com']
    insta_login = 'Onliskill_udm'
    insta_pass = '#PWD_INSTAGRAM_BROWSER:10:1629825416:ASpQAMvl1EAdo0NdRZNcM1/pjlU9rRg4n4cjCM00SDGSV5pDN6XbC93ZbYN67HUOHkXZnGGe2gIWPU2qtQY0HAkIjR5U5syu+lv8qtqeI7cyy2ua6WmBV6AngVo1apn3eJ6O3UAFVgb+q5HtHsQ='
    insta_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    user_parse = 'ai_machine_learning'
    posts_hash = '8c2a529969ee035a5063f2fc8602a0fd'
    graphql_url = 'https://www.instagram.com/graphql/query/?'



    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(self.insta_login_link,
                                 method='POST',
                                 callback=self.user_login,
                                 formdata={'username': self.insta_login,
                                           'enc_password': self.insta_pass},
                                 headers={'X-CSRFToken': csrf})

    def user_login(self, response: HtmlResponse):
        j_body = response.json()
        if j_body['authenticated']:
            yield response.follow(f'/{self.user_parse}',
                                  callback=self.user_data_parse,
                                  cb_kwargs={'username': self.user_parse})


    def user_data_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {
            'id': user_id,
            'first': 12
        }
        url_posts = f'{self.graphql_url}query_hash={self.posts_hash}&{urlencode(variables)}'

        yield response.follow(url_posts,
                              callback=self.user_posts_parse,
                              cb_kwargs={'username': username,
                                         'user_id': user_id,
                                         'variables': deepcopy(variables)}
                              )

    def user_posts_parse(self, response: HtmlResponse, username, user_id, variables):
        if response.status == 200:
            j_data = response.json()
            page_info = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('page_info')
            if page_info.get('has_next_page'):
                variables['after'] = page_info.get('end_cursor')
                url_posts = f'{self.graphql_url}query_hash={self.posts_hash}&{urlencode(variables)}'
                yield response.follow(url_posts,
                                      callback=self.user_posts_parse,
                                      cb_kwargs={'username': username,
                                                 'user_id': user_id,
                                                 'variables': deepcopy(variables)})

            posts = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('edges')
            for post in posts:
                item = InstaparserItem(user_id=user_id,
                                       username=username,
                                       picture=post.get('node').get('display_url'),
                                       likes=post.get('node').get('edge_media_preview_like').get('count'),
                                       post_data=post.get('node')
                                       )
                yield item

    #Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    #Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')