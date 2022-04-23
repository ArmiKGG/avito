from utils import *
import gc
from flask import Flask, request, make_response
from flask_restful import Resource, Api
gc.enable()


app = Flask(__name__)
api = Api(app)


class Status(Resource):
    def get(self):
        return make_response({'status': True}, 200)


class AutoRuParser(Resource):
    def get(self):
        url = request.get_json()['url']
        url_checked = check_url(url)
        if url_checked:
            return make_response(url_checked, 400)

        driver = prepare_driver()

        client = mongo_client()
        retry = client.auto_ru.retry
        auto_info = client.auto_ru.auto_info

        driver.get(url)
        inner_HTML = driver.page_source.lower()

        check_captcha_auto = check_captcha(driver, inner_HTML, url, retry, client)
        if check_captcha_auto['code'] != 200:
            del check_captcha_auto['code']
            return make_response(check_captcha_auto, 400)
        try:
            ready_data = []
            all_links = get_all_links(driver, auto_info)
            process_links(all_links, driver, url, client, auto_info, ready_data, retry)
            driver.quit()
            client.close()
            return make_response({'catalog': ready_data}, 200)
        except Exception as e:
            print(f"error {e}")
            driver.quit()
            client.close()
            return make_response({'status': f'error {e}'}, 400)


api.add_resource(AutoRuParser, '/api/auto_ru/router')
api.add_resource(Status, '/api/auto_ru/health')

if __name__ == '__main__':
    app.run()
