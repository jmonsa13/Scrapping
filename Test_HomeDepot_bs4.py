# Python project for pricing scripping of different sites
# Creado por: Juan Monsalvo

# TEST FOR HOMEDEPOT
# ----------------------------------------------------------------------------------------------------------------------
# Libraries import
# ----------------------------------------------------------------------------------------------------------------------
import os
import time
import datetime
import pandas as pd
import numpy as np
import locale


import requests
from urllib.parse import urlencode
from bs4 import BeautifulSoup
# ----------------------------------------------------------------------------------------------------------------------
# Setting the local currency, using DE to be able to have thousands sep = . and decimal point = ,
locale.setlocale(locale.LC_NUMERIC, "de_DE")

# Obtener definiciones de la configuración actual
configuracion = locale.localeconv()

# Path definition of the .csv file
fecha = datetime.datetime.today()
output_path_toilet = './XX_Data/Homedepot_test-' + str(fecha.year) + '_' + str(fecha.month) + '.csv'
# ----------------------------------------------------------------------------------------------------------------------
# General Variables
# url = 'https://www.homedepot.com/'
url1 = 'https://www.homedepot.com/p/American-Standard-Cadet-3-Tall-Height-10-in-Rough-In-2-piece-1-28-GPF-Single-' \
      'Flush-Elongated-Toilet-in-White-Seat-Included-3378AB128ST-020/206888651'

url2 = 'https://www.homedepot.com/p/Glacier-Bay-2-piece-1-1-GPF-1-6-GPF-High-Efficiency-Dual-Flush-Complete-' \
       'Elongated-Toilet-in-White-Seat-Included-N2316/100676582'

url3 = 'https://www.homedepot.com/p/Glacier-Bay-2-piece-1-1-GPF-1-6-GPF-Dual-Flush-Round-Toilet-in-White-N2428R-' \
       'DF/202862164'

url_list = [url1, url2, url3]

NUM_RETRIES = 5

# Tell scraper to use Scraper API as the proxy
# PROXY = 'Seljmonsa13:W2a9FxY@68.67.198.26:45785'
# proxies = {'http': "http://" + PROXY, 'https': "https://" + PROXY}

API_KEY = '48f0187b8c701cbe3479abbf6e6f9d81'

# Waiting time between request
delays = [7, 4, 6, 2, 8, 3]

# ----------------------------------------------------------------------------------------------------------------------
# Beautiful soup
# ----------------------------------------------------------------------------------------------------------------------
headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}

# Scrapping the information of every url
data = []
for url in url_list:
    # send request to scraperapi, and automatically retry failed requests
    params = {'api_key': API_KEY, 'url': url}


    for i in range(NUM_RETRIES):
        # Random Wait between request
        delay = np.random.choice(delays)
        time.sleep(delay)
        try:
            #response = requests.get(url, proxies=proxies, headers=headers)
            response = requests.get('http://api.scraperapi.com/', params=urlencode(params))
            #response = requests.get(url,  headers=headers)

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

        soup: BeautifulSoup = BeautifulSoup(response.content, "html.parser")

        # Collecting the name and product tipe
        brand_name = soup.find("span", class_="product-details__brand--link").text.strip()
        product_name = soup.find("h1", class_="product-details__title").text.strip()

        # Collecting the price
        price_raw = soup.find("div", class_="price").text.strip()[:-2]
        price_clean = int(locale.atof(price_raw.strip("$")))

        # Collecting the sku
        sku_ref_bar = soup.find_all("h2", class_="product-info-bar__detail--7va8o")

        for item_raw in sku_ref_bar:
            item = item_raw.text.strip().split(" #")[0]
            if item == "Store SKU":
                sku_ref = item_raw.text.strip().split(" #")[1]

        # Collecting the image
        image_raw = soup.find("a", class_="mediagallery__anchor")
        image_html = image_raw.find("img")
        URL_img = image_html["src"]

        # ------------------------------------------------------------------------------------------------------------------
        # Message display
        print("Recopilando la información de {}".format(url))
        print("La marca es la: {}".format(brand_name))
        print("El sanitario es el: {}".format(product_name))
        print("El sku es el: {}".format(sku_ref))
        print("El precio es: {} USD".format(price_clean))
        print(URL_img)
        print("\n")
        # ------------------------------------------------------------------------------------------------------------------
        # Appending the item in a list
        information = [datetime.datetime.today().date(), brand_name, "Sanitario", brand_name, product_name, sku_ref,
                       price_clean, "USD", "homedepot.com", "Si", url, URL_img]

        data.append(information)

    # Creating the dataframe
    df = pd.DataFrame(data, columns=["Fecha", "Marca", "Tipo", "Familia", "Producto", "SKU", "Precio", "Moneda",
                                     "Market_Place", "Stock", "URL", "Image_url"])

# Saving the file in a .csv file
df.to_csv(output_path_toilet, mode='a', header=not os.path.exists(output_path_toilet), index=False)


