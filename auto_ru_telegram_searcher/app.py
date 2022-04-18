import grequests

urls = [
    'http://127.0.0.1:5000/api/auto_ru/router?url=https://auto.ru/cars/used/sale/mazda/3/1114818216-08bdfeda/'
] * 3

rs = (grequests.get(u) for u in urls)

rs = grequests.map(rs)
for i in rs:
    print(i.json())