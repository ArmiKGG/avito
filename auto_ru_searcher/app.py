import concurrent
import os
import pickle
from datetime import datetime

from bs4 import BeautifulSoup
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from flask import Flask, request, make_response
from flask_restful import Resource, Api
from utils import *
import pymongo
import requests

app = Flask(__name__)
api = Api(app)


def mongo_client():
    client = pymongo.MongoClient(f'mongodb+srv://{os.environ.get("MONGO_LOG")}:{os.environ.get("MONGO_PAS")}@cluster0'
                                 f'.qmeif.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
    return client


def do_job(link, processed, unprocessed):
    print(link, flush=True)
    data = requests.get(
        f'http://{os.environ.get("API_HOST")}:{os.environ.get("API_PORT")}/api/auto_ru/router',
        params={'url': link}, timeout=20)
    if data.status_code == 200:
        print({"datetime": datetime.today().replace(microsecond=0), **data.json()}, flush=True)
        processed.insert_one({"datetime": datetime.today().replace(microsecond=0), **data.json()})
    else:
        print({"datetime": datetime.today().replace(microsecond=0), **data.json()}, flush=True)
        unprocessed.insert_one({"datetime": datetime.today().replace(microsecond=0), **data.json()})


class Status(Resource):
    def get(self):
        return make_response({'status': True}, 200)


class AutoRuParserGetAll(Resource):
    def get(self):
        url = request.args.get('url')
        if not url:
            bad_link = {'status': 'not url',
                        'url': url}
            return make_response(bad_link, 400)

        if 'cars/used' not in url or 'page=' not in url:
            bad_link = {'status': 'Not auto.ru/cars/used link or page=1..n not provided',
                        'url': url}
            return make_response(bad_link, 400)
        client = mongo_client()
        unprocessed = client.auto_ru.badlinks
        processed = client.auto_ru.data
        driver = prepare_driver()
        if os.path.exists('cookies/auto_ru_cookies.pkl'):
            cookies = pickle.load(open("cookies/auto_ru_cookies.pkl", "rb"))
            for cookie in cookies:
                driver.add_cookie(cookie)

        gen_links = [url.split('page=')[0] + f"page={i}" for i in range(1, 30)]

        for i in gen_links:
            driver.get(i)
            if 'captcha' in driver.page_source.lower():
                captcha_message = {'status': 'Yandex Captcha found, go to session page and resolve it host:7900',
                                   'url': url}
                driver.quit()
                client.close()
                return make_response(captcha_message, 400)
            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a.ListingItemTitle__link")))
                inner_HTML = driver.page_source
                auto = AutoRu(BeautifulSoup(inner_HTML, 'lxml'), inner_HTML)
                all_links = auto.get_catalog_links()
                print(all_links)
                with concurrent.futures.ThreadPoolExecutor(
                        max_workers=3) as executor:
                    future_to_files = {executor.submit(do_job, link, processed, unprocessed): link for link in
                                       all_links}
                    for future in concurrent.futures.as_completed(future_to_files):
                        url = future_to_files[future]
                        try:
                            data = future.result()
                            print('%r data: %s' % (url, exc))
                        except Exception as exc:
                            print('%r generated an exception: %s' % (url, exc))
                        else:
                            print('%r page is %d bytes' % (url, len(data)))

                pickle.dump(driver.get_cookies(), open("cookies/auto_ru_cookies.pkl", "wb"))
                driver.quit()
                client.close()
                return make_response({'status': f'job done'}, 200)
            except Exception as e:
                print(e, flush=True)
                driver.quit()
                client.close()
                return make_response({'status': f'error {e}'}, 400)


class AutoRuParserMonitor(Resource):
    def get(self):
        url = request.args.get('url')
        if not url:
            bad_link = {'status': 'not url',
                        'url': url}
            return make_response(bad_link, 400)

        if 'auto.ru' not in url or 'page=' not in url:
            bad_link = {'status': 'Not auto.ru/ link or page=1..n not provided',
                        'url': url}
            return make_response(bad_link, 400)
        driver = prepare_driver()
        if os.path.exists('cookies/auto_ru_cookies.pkl'):
            cookies = pickle.load(open("cookies/auto_ru_cookies.pkl", "rb"))
            for cookie in cookies:
                driver.add_cookie(cookie)
        client = mongo_client()
        unprocessed = client.auto_ru.badlinks
        processed = client.auto_ru.data
        driver.get(url)
        if 'captcha' in driver.page_source.lower():
            captcha_message = {'status': 'Yandex Captcha found, go to session page and resolve it host:7900',
                               'url': url}
            driver.quit()
            client.close()
            return make_response(captcha_message, 400)
        try:
            WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.ListingItemTitle__link")))
            inner_HTML = driver.page_source
            auto = AutoRu(BeautifulSoup(inner_HTML, 'lxml'), inner_HTML)
            all_links = auto.get_catalog_links()
            print(all_links, flush=True)
            with concurrent.futures.ThreadPoolExecutor(
                    max_workers=3) as executor:
                future_to_files = {executor.submit(do_job, link, processed, unprocessed): link for link in
                                   all_links}
                for future in concurrent.futures.as_completed(future_to_files):
                    url = future_to_files[future]
                    try:
                        data = future.result()
                        print('%r data: %s' % (url, exc))
                    except Exception as exc:
                        print('%r generated an exception: %s' % (url, exc))
                    else:
                        print('%r page is %d bytes' % (url, len(data)))
            pickle.dump(driver.get_cookies(), open("cookies/auto_ru_cookies.pkl", "wb"))
            driver.quit()
            client.close()
            return make_response({'status': 'job is done'}, 200)
        except Exception as e:
            print(e, flush=True)
            driver.quit()
            client.close()
            return make_response({'status': f'error {e}'}, 400)


api.add_resource(AutoRuParserGetAll, '/api/auto_ru/get_all')
api.add_resource(AutoRuParserMonitor, '/api/auto_ru/monitor')
api.add_resource(Status, '/api/auto_ru/status')

if __name__ == '__main__':
    app.run(debug=True, port=5050)
