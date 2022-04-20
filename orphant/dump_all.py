import requests
import gc

gc.enable()

import argparse

# Instantiate the parser
parser = argparse.ArgumentParser(description='Optional app description')
parser.add_argument('start', type=int,
                    help='start')

parser.add_argument('end', type=int,
                    help='end')

args = parser.parse_args()
for i in range(args.start, args.end):
    resp = requests.get(f'http://127.0.0.1:5000/api/auto_ru/router', json={'url': f"https://auto.ru/moskva/cars/used/do-1000000/?sort=cr_date-desc&seller_group=PRIVATE&catalog_equipment=esp&catalog_filter=mark%3DMAZDA&catalog_filter=mark%3DHYUNDAI&catalog_filter=mark%3DFORD&catalog_filter=mark%3DHONDA&catalog_filter=mark%3DMERCEDES&catalog_filter=mark%3DKIA&output_type=table&page={i}"},  timeout=1200)
    if resp.status_code == 400:
        break
    print(i, resp.status_code, flush=True)

