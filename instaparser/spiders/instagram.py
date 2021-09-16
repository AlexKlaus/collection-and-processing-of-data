import scrapy
import re
import json
from scrapy.http import HtmlResponse
from instaparser.items import InstaparserItem
from passw import login, passw


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com']
    insta_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    user_parse = ['make3dprint_spb', 'rollomaticsa']
    posts_hash = '8c2a529969ee035a5063f2fc8602a0fd'
    graphql_url = 'https://www.instagram.com/graphql/query/?'
    insta_login = login
    insta_pass = passw


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
            for user in self.user_parse:
                yield response.follow(f'/{user}',
                                      callback=self.user_data_parse,
                                      cb_kwargs={'username': user})


    def user_data_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        url_followers = f'https://i.instagram.com/api/v1/friendships/{user_id}/followers/?' \
                        f'count=12&search_surface=follow_list_page'
        url_followings = f'https://i.instagram.com/api/v1/friendships/{user_id}/following/?count=12'
        yield response.follow(url_followers,
                              callback=self.followers_parse,
                              cb_kwargs={'username': username})
        yield response.follow(url_followings,
                              callback=self.followings_parse,
                              cb_kwargs={'username': username})


    def followers_parse(self, response: HtmlResponse, username):
        if response.status == 200:
            j_data = response.json()
            if j_data.get('next_max_id'):
                yield response.follow(response.url + f"&max_id={j_data['next_max_id']}",
                                      callback=self.followers_parse,
                                      cb_kwargs={'username': username})
            for user in j_data['users']:
                item = InstaparserItem(followers_or_followings='followers',
                                       parsed_user=username,
                                       name=user.get('full_name'),
                                       id=user.get('pk'),
                                       picture=user.get('profile_pic_url'))
                yield item

    def followings_parse(self, response: HtmlResponse, username):
        if response.status == 200:
            j_data = response.json()
            if j_data.get('next_max_id'):
                yield response.follow(response.url + f"&max_id={j_data['next_max_id']}",
                                      callback=self.followings_parse,
                                      cb_kwargs={'username': username})
            for user in j_data['users']:
                item = InstaparserItem(followers_or_followings='followings',
                                       parsed_user=username,
                                       name=user.get('full_name'),
                                       id=user.get('pk'),
                                       picture=user.get('profile_pic_url'))
                yield item

    # Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    # Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
