FROM python:3.8

WORKDIR /app

COPY requirements.txt .
COPY utils.py .
COPY wsgi.py .
COPY app.py .
COPY cookies ./cookies
COPY rundinant_modules ./rundinant_modules

RUN pip install -r requirements.txt


CMD gunicorn --worker-class gevent \
  --workers 20 \
  --bind 0.0.0.0:5000 \
  --timeout 0 \
  --limit-request-line 0 \
  --preload \
  wsgi:app
