#! /usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import pymysql.cursors

from bs4 import BeautifulSoup

import re

URL = 'https://kolesa.kz/cars/region-almatinskaya-oblast/?auto-emergency=2'

HEADERS = {'user-agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36', 'accept': '*/*'}

HOST = 'https://kolesa.kz'

# Укажите токен телеграм
telegram_token = 'bot1150717483:AAH-ebKbiOuVjpI8uqe9e3s-BLawTl7uoBU'

# Укажите чат id в который необходимо отправлять данные
telegram_chat_id = '74768964'

base_url_telegram = 'https://api.telegram.org/'+telegram_token+'/sendMessage'

conn = pymysql.connect(
    host='db4free.net',
    port=3306,
    user='kolesa',
    password='Kolesa2020',
    db='kolesa',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)
cursor = conn.cursor()
'''cursor.execute("""CREATE TABLE IF NOT EXISTS kolesa (
    data_id TEXT,
    link TEXT,
    title TEXT
) """)
conn.commit()
'''

def get_html(url, params=None):
    r = requests.get(url,headers=HEADERS,params=params)
    return r

def get_pagecount(html):
    soup = BeautifulSoup(html,'html.parser')
    items = soup.select(".paginator ul span")
    pages = []
    for item in items:
        pages.append(
            item.text
        )
    return int(pages[-1])

cars = []

def get_content(html):
    soup = BeautifulSoup(html,'html.parser')
    items = soup.find_all('div', class_='vw-item')

    
    for item in items:
        cars.append({
            'data_id' : item.get('data-id'),
            'title' : item.find('span', class_='a-el-info-title').get_text(), 
            'link' : HOST + item.find('a', class_='ddl_product_link').get('href')
        })
    return cars    
    print(cars)
    #print(len(cars))




def send_to_db(data_id, link, title):
    cursor.execute("""INSERT INTO kolesa (data_id, link, title) VALUES (%s,%s,%s)""", [data_id, link, title])
    conn.commit()
    print(cursor)

def process_send(cars):
    for car in cars:
        elem_exists = check_item_db(car['data_id'])
        # проверяем есть ли данный элемент в БД
        if not elem_exists:
            # Отправка в БД
            send_to_db(car['data_id'], car['link'], car['title'])
            # Отправка в телеграм
            send_telegram(car['link'], car['title'])

def check_item_db(data_id):
    sql = 'SELECT * FROM kolesa WHERE data_id = %s'
    cursor.execute(sql, [(int(data_id))])
    return cursor.fetchone()

def send_telegram(title, link):
    params = {'chat_id': telegram_chat_id,'text': title+'\n'+link}
    session = requests.Session()
    response = session.get(base_url_telegram, params=params)
    print(response.url)
    print(response.status_code)



def parse():
    html = get_html(URL)
    if html.status_code == 200:
        cars = []
        pages_count = get_pagecount(html.text)
        for page in range(1, pages_count + 1):
            html = get_html(URL, params={'page': page})
            #print(html.url)
            cars.extend(get_content(html.text))
            
        #print(cars)
    else:
        print('Error')

parse()
process_send(cars)


