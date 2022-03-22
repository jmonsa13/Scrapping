# Python project for pricing scripping of different sites
# Creado por: Juan Monsalvo

# TEST FOR HOMEDEPOT

# ----------------------------------------------------------------------------------------------------------------------
# Libraries import
# ----------------------------------------------------------------------------------------------------------------------
import time
from bs4 import BeautifulSoup

from seleniumwire import webdriver
#from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# General Variables
API_KEY = '48f0187b8c701cbe3479abbf6e6f9d81'
url = 'https://www.homedepot.com/'
# url = 'https://corona.co/productos/asientos-sanitarios/asiento-prestigio-cierre-suave-alongado-blanco/p/609201001'
NUM_RETRIES = 5

# Tell scraper to use Scraper API as the proxy
PROXY = '18.118.128.148:80'
proxies = {'http': f'http://scraperapi:{API_KEY}@proxy-server.scraperapi.com:8001',
           'https': f'http://scraperapi:{API_KEY}@proxy-server.scraperapi.com:8001',}
# proxies = {'http': "http://" + PROXY, 'https': "https://" + PROXY}

proxy_options = {'proxy': proxies}

# Waiting time between request
delays = [7, 4, 6, 2, 8, 3]

# ----------------------------------------------------------------------------------------------------------------------
# Selenium
# ----------------------------------------------------------------------------------------------------------------------
# Configuration of Chrome
options = webdriver.ChromeOptions()

options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
# options.add_argument('--headless')
options.add_argument("start-maximized")
#options.add_argument('--proxy-server=%s' % PROXY)

# Setting the WebBrowser
s = Service(ChromeDriverManager().install())

# Loading the WebBrowser
# driver = webdriver.Chrome(service=s, options=options)
driver = webdriver.Chrome(service=s, options=options, seleniumwire_options=proxy_options)

driver.get(url)

time.sleep(10)
#price = driver.find_element(By.XPATH('//div[@class="name"]'))
#print(price)
# ----------------------------------------------------------------------------------------------------------------------
# Selenium and beautifulsoup
html_response = driver.page_source
soup = BeautifulSoup(html_response, "html.parser")

# product_name = soup.find("div", class_="name").text.strip()
# print("Product name using Selenium and BeautifulSoup {}".format(product_name))


