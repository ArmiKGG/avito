FROM python:3.8

WORKDIR /app

COPY requirements.txt .
COPY utils.py .
COPY wsgi.py .
COPY app.py .
COPY cookies ./cookies

RUN pip install -r requirements.txt


CMD gunicorn --worker-class gevent \
  --workers 20 \
  --bind 0.0.0.0:5050 \
  --timeout 50 \
  --limit-request-line 0 \
  --preload \
  --log-level debug\
  wsgi:app
