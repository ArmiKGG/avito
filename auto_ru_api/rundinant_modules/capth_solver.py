from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from python_anticaptcha import AnticaptchaClient, NoCaptchaTaskProxylessTask
import re
import os
import time
import requests

# api_key = 'anti-captcha' google recaptcha
# site_key = ''  # grab from site
#
# client = AnticaptchaClient(api_key)
# task = NoCaptchaTaskProxylessTask(url, site_key)
# job = client.createTask(task)
# print("Waiting to solution by Anticaptcha workers")
# job.join()
# # Receive response
# response = job.get_solution_response()
# print("Received solution", response)
#
# # Inject response in webpage
# driver.execute_script('document.getElementById("g-recaptcha-response").innerHTML = "%s"' % response)
#
# # Wait a moment to execute the script (just in case).
# time.sleep(1)
#
# # Press submit button
# driver.find_element_by_xpath('//button[@type="submit" and @class="btn-std"]').click()