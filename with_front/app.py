import requests
import schedule


url = "https://auto.ru/moskva/cars/used/?year_from=2012&price_to=1299999&catalog_filter=mark%3DINFINITI&catalog_filter=mark%3DSUZUKI&catalog_filter=mark%3DLAND_ROVER&catalog_filter=mark%3DVOLKSWAGEN&catalog_filter=mark%3DCHEVROLET&catalog_filter=mark%3DCITROEN&catalog_filter=mark%3DPORSCHE&catalog_filter=mark%3DSKODA&catalog_filter=mark%3DOPEL&catalog_filter=mark%3DMITSUBISHI&catalog_filter=mark%3DMAZDA&catalog_filter=mark%3DLEXUS&catalog_filter=mark%3DMINI&catalog_filter=mark%3DRENAULT&catalog_filter=mark%3DTOYOTA&catalog_filter=mark%3DFORD&catalog_filter=mark%3DHYUNDAI&catalog_filter=mark%3DBMW&catalog_filter=mark%3DNISSAN&catalog_filter=mark%3DKIA&catalog_filter=mark%3DVOLVO&catalog_filter=mark%3DHONDA&catalog_filter=mark%3DAUDI&catalog_filter=mark%3DMERCEDES&seller_group=PRIVATE&sort=cr_date-desc&top_days=3&page=1"


def job():
    data = requests.get("{}:{}/api/auto_ru/router".format("http://51.250.104.136", "5000"), json={"url": url})
    print(data.json(), flush=True)


schedule.every(2).minutes.do(job)

while True:
    schedule.run_pending()
