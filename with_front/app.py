import os
import time

import requests
import schedule
from flask import Flask, render_template, request


app = Flask(__name__)

PORT = 5000


@app.route('/', methods=["GET", "POST"])
def index():
    return render_template('index.html')


@app.route('/add_env', methods=["GET", "POST"])
def addenv():
    if request.method == 'POST':
        os.environ['MONITOR_URL'] = request.form.get("url")
        if os.environ.get('MONITOR_URL'):
            return {"status": True}


@app.route('/monitor', methods=["GET", "POST"])
def monitor():
    if request.method == 'POST':
        url = os.environ.get('MONITOR_URL')
        if not url:
            return {"status": False}

        def job():
            data = requests.get("{}:{}".format(os.environ['ROUTER'], os.environ['ROUTER_PORT']), json={"url": url},
                                timeout=600)
            print(data)
        schedule.every(5).minutes.do(job)

        while True:
            schedule.run_pending()
            time.sleep(5)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
