import requests
from selenium import webdriver
import os
import time
from datetime import datetime
import pymongo
from bs4 import BeautifulSoup
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pickle
from dotenv import load_dotenv

load_dotenv()


def prepare_driver():
    options = webdriver.FirefoxOptions()
    options.add_argument('--disable-gpu')
    options.add_argument(f'--host=http://{os.environ.get("STARTING_PAGE")}')
    driver = webdriver.Remote(
        command_executor=f'http://{os.environ.get("ROUTER")}:{os.environ.get("ROUTER_PORT")}/wd/hub', options=options)
    if os.path.exists('cookies/auto_ru_cookies.pkl'):
        cookies = pickle.load(open("cookies/auto_ru_cookies.pkl", "rb"))
        for cookie in cookies:
            print(f'cookie added {cookie}!')
            driver.add_cookie(cookie)
    return driver


class AutoRu:
    def __init__(self, soup, data):
        self.soup = soup
        self.data = data

    def get_comment(self):
        data = self.soup.find(class_='CardDescriptionHTML')
        if data:
            return data.text
        return None

    def get_images(self):
        data = self.soup.find_all(class_='ImageGalleryDesktop__thumb')
        data = ['https://' + i['src'].replace('//', '').replace('small', '1200x900n') for i in data]
        if data:
            return data
        return None

    def get_tag(self):
        data = self.soup.find(class_='OfferPriceBadge')
        if data:
            return data.text
        return None

    def get_params(self):
        data = self.soup.select('ul.CardInfo li')
        all_jsonned = {}
        for dat in data:
            dexter = dat.find_all('span')
            all_jsonned[dexter[0].text] = dexter[1].text.replace('\xa0', ' ')
        return all_jsonned

    def get_price(self):
        data = self.soup.select_one('span.OfferPriceCaption__price')
        if data:
            return data.text
        return None

    def get_phone(self):
        data = self.soup.select_one('a.SellerPopup__phoneNumber')
        if data:
            return data.text
        return None

    def get_catalog_links(self):
        data = [i['href'] for i in self.soup.select('a.ListingItemTitle__link')]
        if data:
            return data
        return []

    def get_title(self):
        data = self.soup.select_one('h1.CardHead__title')
        if data:
            return data.text
        return None

    def get_creation_date(self):
        data = self.soup.select_one('div.CardHead__creationDate')
        if data:
            return data['title']
        return None

    def get_views(self):
        data = self.soup.select_one('div.CardHead__views')
        if data:
            return data.text
        return None


def mongo_client():
    client = pymongo.MongoClient(f'mongodb+srv://{os.environ.get("MONGO_LOG")}:{os.environ.get("MONGO_PAS")}@cluster0'
                                 f'.qmeif.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
    # client = pymongo.MongoClient('localhost', 27017)
    print('Mongo connected!')
    return client


def check_url(url):
    if not url:
        bad_link = {'status': 'not url',
                    'url': url}
        print(f'bad link {url}!')
        return bad_link

    if 'auto.ru' not in url or 'page=' not in url:
        bad_link = {'status': 'Not auto.ru link or page=1..n not provided',
                    'url': url}
        print(f'Not auto.ru {url}!')
        return bad_link
    return None


def check_captcha(driver, inner_HTML, url, retry, client):
    if 'страница не найдена' in inner_HTML.lower():
        nopage = {'status': 'no page',
                  'url': url}
        print(f'captcha {nopage}!')
        return {**nopage, "code": 400}
    if 'captcha' in inner_HTML:
        captcha_message = {'status': 'Yandex Captcha found',
                           'url': url}
        print(f'captcha {url}!')
        if not list(retry.find({'url': url})):
            print(f'added to unprocessed {url}!')
            retry.insert_one({"datetime": datetime.today().replace(microsecond=0), "url": url})

        print("resolve captcha manually in 15m!!!!")
        print("resolve captcha manually in 15m!!!!")
        print("resolve captcha manually in 15m!!!!")
        print("resolve captcha manually in 15m!!!!")
        print("resolve captcha manually in 15m!!!!")
        print("resolve captcha manually in 15m!!!!")
        time.sleep(900)
        if 'captcha' not in driver.page_source.lower():
            print(f'captcha {url}!')
            pickle.dump(driver.get_cookies(), open("cookies/auto_ru_cookies.pkl", "wb"))
            return {'code': 200}
        else:
            driver.quit()
            client.close()
            return {**captcha_message, "code": 404}
    return {"code": 200}


def get_all_links(driver, auto_info):
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a.ListingItemTitle__link")))
    inner_HTML = driver.page_source
    auto = AutoRu(BeautifulSoup(inner_HTML, 'lxml'), inner_HTML)
    all_links = auto.get_catalog_links()

    if not all_links:
        print(f"empty list!!!")
        return {'status': 'empty list', "code": 400}
    clean_link = []
    for link in all_links:
        if '?' in link:
            link = link.split('?')[0]
        if not list(auto_info.find({'url': link})):
            clean_link.append(link)

    print(f"links {clean_link}")
    return clean_link


def process_links(all_links, driver, url, client, auto_info, ready_data, retry):
    for link in all_links:
        try:
            if not list(auto_info.find({'url': link})):
                driver.get(link)
                inner_HTML = driver.page_source
                captcha_checker = check_captcha(driver, inner_HTML, url, retry, client)
                if captcha_checker['code'] == 200:
                    print(f"started {link}!!!")
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "button.OfferPhone_button"))).click()

                    phone = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "a.SellerPopup__phoneNumber"))).text

                    inner_HTML = driver.page_source
                    print(f"got {str(inner_HTML[:100])}!!!")
                    auto = AutoRu(BeautifulSoup(inner_HTML, 'lxml'), inner_HTML)

                    if not phone:
                        phone = auto.get_phone()

                    parsed_info = {'tag': auto.get_tag(), 'parameters': auto.get_params(),
                                   'comment': auto.get_comment(),
                                   'images': auto.get_images(), 'phone': phone, 'price': auto.get_price(),
                                   'url': link, 'title_webpage': driver.title, 'title': auto.get_title(),
                                   'views': auto.get_views(), 'date_created': auto.get_creation_date()}
                    text = f"<code>tag</code>: <b>{parsed_info['tag'] if parsed_info['tag'] else 'No tag'}</b>\n\n<code>date_scanned</code>:" \
                           f" <i>{datetime.today().strftime('%Y-%M-%dT%H:%M:%S')}</i>\n\n<code>date_created</code>: <i>{parsed_info['date_created']}</i>\n\n<code>views</code>: <i>{parsed_info['views'] if parsed_info['views'] else 'no views'}</i>\n\n<code>title</code>: <b>{parsed_info['title']}</b>\n\n<code>price</code>: <b>{parsed_info['price']}</b>\n\n<code>phone</code>: {parsed_info['phone']}\n\n<code>info</code>: <i>{parsed_info['title_webpage']}</i>\n\n<code>url</code>: <i>{parsed_info['url']}</i> "
                    resp = requests.post(
                        url='https://api.telegram.org/bot{0}/{1}'.format(
                            "5353011015:AAGCAPVNvOv7qem4NcQqykYA17FgpjcWVO0", "sendMessage"),
                        data={'chat_id': -1001606926823, 'text': text, "parse_mode": "HTML"}
                    )
                    print(f"got {parsed_info['title']} parsed!!! - tg status = {resp.json()}")
                    auto_info.insert_one({"datetime": datetime.today().replace(microsecond=0), **parsed_info})
                    pickle.dump(driver.get_cookies(), open("cookies/auto_ru_cookies.pkl", "wb"))
                    ready_data.append(parsed_info)

        except Exception as e:
            print(f"error {e}")
            bad_button_message = {'status': f'Bad button, link added to broken collection - {e}', 'url': link}
            if not list(retry.find({'url': link})):
                retry.insert_one(
                    {"datetime": datetime.today().replace(microsecond=0), **bad_button_message})
            pickle.dump(driver.get_cookies(), open("cookies/auto_ru_cookies.pkl", "wb"))
            ready_data.append(bad_button_message)
