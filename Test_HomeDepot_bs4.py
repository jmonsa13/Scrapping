# Python project for pricing scripping of different sites
# Creado por: Juan Monsalvo

# TEST FOR HOMEDEPOT

# ----------------------------------------------------------------------------------------------------------------------
# Libraries import
# ----------------------------------------------------------------------------------------------------------------------
import time
import numpy as np

import requests
from bs4 import BeautifulSoup
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# General Variables
API_KEY = '48f0187b8c701cbe3479abbf6e6f9d81'
url = 'https://www.homedepot.com/'
# url = 'https://corona.co/productos/asientos-sanitarios/asiento-prestigio-cierre-suave-alongado-blanco/p/609201001'
NUM_RETRIES = 5

# Tell scraper to use Scraper API as the proxy
PROXY = 'Seljmonsa13:W2a9FxY@185.240.120.20:45785'
proxies = {'http': "http://" + PROXY, 'https': "https://" + PROXY}

# Waiting time between request
delays = [7, 4, 6, 2, 8, 3]
# ----------------------------------------------------------------------------------------------------------------------
# Beautiful soup
# ----------------------------------------------------------------------------------------------------------------------
headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}

# send request to scraperapi, and automatically retry failed requests
for i in range(NUM_RETRIES):
    # Random Wait between request
    delay = np.random.choice(delays)
    time.sleep(delay)
    try:
        response = requests.get(url, proxies=proxies, headers=headers)
        # response = requests.get(url,  headers=headers)

        print("Intento numero {}".format(i))
        print(response)
        if response.status_code in [200, 404]:
            # escape for loop if the API returns a successful response
            break
    except requests.exceptions.ConnectionError:
        response = ''
        print("ConnectionError")

# parse data if 200 status code (successful response)
if response.status_code == 200:
  # Example: parse data with beautifulsoup
  print("Exito!!!")

  soup = BeautifulSoup(response.content, "html.parser")
  print(soup)
  # quotes_sections = soup.find_all('div', class_="quote")
