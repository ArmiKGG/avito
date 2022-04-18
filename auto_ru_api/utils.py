from selenium import webdriver
import os


def prepare_driver():
    options = webdriver.FirefoxOptions()
    options.add_argument('--disable-gpu')
    options.add_argument(f'--host={os.environ.get("STARTING_PAGE")}')
    driver = webdriver.Remote(command_executor=f'http://{os.environ.get("ROUTER")}:{os.environ.get("ROUTER_PORT")}/wd/hub', options=options)
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

    def get_phone(self):
        data = self.soup.select_one('a.SellerPopup__phoneNumber')
        if data:
            return data.text

