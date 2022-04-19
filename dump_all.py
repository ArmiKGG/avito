import requests
import gc

gc.enable()
for i in range(1, 10):
    resp = requests.get(f'http://127.0.0.1:5000/api/auto_ru/router', json={'url': f"https://auto.ru/moskva/cars/used/?year_from=2009&km_age_to=350000&catalog_filter=mark%3DVOLKSWAGEN&catalog_filter=mark%3DMAZDA&catalog_filter=mark%3DTOYOTA&catalog_filter=mark%3DFORD&catalog_filter=mark%3DVOLVO&sort=cr_date-desc&top_days=2&output_type=table&page={i}"},  timeout=1200)
    if resp.status_code == 400:
        break
    print(i, resp.status_code, flush=True)
