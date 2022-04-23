FROM python:3.8

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD gunicorn --worker-class gevent \
  --workers 20 \
  --bind 0.0.0.0:80 \
  --timeout 0 \
  --limit-request-line 0 \
  --preload \
  wsgi:app
