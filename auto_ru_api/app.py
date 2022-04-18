import os
from datetime import datetime
import pymongo
from bs4 import BeautifulSoup
from flask import Flask, request, make_response
from flask_restful import Resource, Api
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils import *
from selenium.webdriver.common.by import By
import pickle

app = Flask(__name__)
api = Api(app)


def mongo_client():
    client = pymongo.MongoClient(f'mongodb+srv://{os.environ.get("MONGO_LOG")}:{os.environ.get("MONGO_PAS")}@cluster0'
                                 f'.qmeif.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
    return client


class Status(Resource):
    def get(self):
        return make_response({'status': True}, 200)


class AutoRuParser(Resource):
    def get(self):
        url = request.args.get('url')

        if not url:
            return make_response({'status': 'no url'}, 400)
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
            captcha_message = {'status': 'Yandex Captcha found',
                               'url': url}
            if not unprocessed.find({'url': url}):
                unprocessed.insert_one({"datetime": datetime.today().replace(microsecond=0), **unprocessed})
            # driver.quit()
            # client.close()
            return make_response(captcha_message, 400)

        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button.OfferPhone_button"))).click()

            phone = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.SellerPopup__phoneNumber"))).text

            inner_HTML = driver.page_source
            auto = AutoRu(BeautifulSoup(inner_HTML, 'lxml'), inner_HTML)

            if not phone:
                phone = auto.get_phone()

            parsed_info = {'tag': auto.get_tag(), 'parameters': auto.get_params(), 'comment': auto.get_comment(),
                           'images': auto.get_images(), 'phone': phone, 'price': auto.get_price()}
            print(parsed_info, flush=True)
            if not processed.find({'url': url}):
                processed.insert_one({"datetime": datetime.today().replace(microsecond=0), **parsed_info})
            pickle.dump(driver.get_cookies(), open("cookies/auto_ru_cookies.pkl", "wb"))
            driver.quit()
            client.close()
            return make_response(parsed_info, 200)

        except Exception as e:
            print(e)
            bad_button_message = {'status': f'Bad button, link added to broken collection - {e}', 'url': url}
            if not unprocessed.find({'url': url}):
                unprocessed.insert_one({"datetime": datetime.today().replace(microsecond=0), **bad_button_message})
            # driver.quit()
            # client.close()
            return make_response(bad_button_message, 400)


api.add_resource(AutoRuParser, '/api/auto_ru/router')
api.add_resource(Status, '/api/auto_ru/health')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
