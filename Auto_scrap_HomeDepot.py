# Python project for pricing scripping of different sites
# Creado por: Juan Monsalvo

# FOR HOMEDEPOT
# ----------------------------------------------------------------------------------------------------------------------
# Libraries import
# ----------------------------------------------------------------------------------------------------------------------
import datetime
import locale
import os
import time

import numpy as np
import pandas as pd

import requests
from urllib.parse import urlencode
from bs4 import BeautifulSoup

# ----------------------------------------------------------------------------------------------------------------------
# Configuration and Global Variables
# ----------------------------------------------------------------------------------------------------------------------
# Setting the local currency, using DE to be able to have thousands sep = . and decimal point = ,
locale.setlocale(locale.LC_NUMERIC, "de_DE")

# Obtener definiciones de la configuración actual
configuracion = locale.localeconv()

# Path definition of the .csv file
fecha = datetime.datetime.today()
output_path_toilet = './XX_Data/Homedepot_toilet-' + str(fecha.year) + '_' + str(fecha.month) + '.csv'

# Path for loading the URL sites
url_path_toilet = './XX_Url/HomeDepot_URL.csv'

# Number of retry
NUM_RETRIES = 5

# Tell scraper to use Scraper API as the proxy
API_KEY = '48f0187b8c701cbe3479abbf6e6f9d81'

# Waiting time between request
delays = [1, 4, 8, 2, 5, 3]

# Header for beautiful soup
headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}


# ----------------------------------------------------------------------------------------------------------------------
# Function Definition
# ----------------------------------------------------------------------------------------------------------------------
def homedepot_data(url_link, soup_html):
    """
    Programa que toma la información general de una pagina de producto del market place de HomeDepot
    """

    # Collecting the name and product tipe
    brand_name = soup_html.find("span", class_="product-details__brand--link").text.strip()
    product_name = soup_html.find("h1", class_="product-details__title").text.strip()

    if "bowl only" in product_name.lower():
        product_format = "Bowl"
    elif "tank only" in product_name.lower():
        product_format = "Tank"
    else:
        product_format = "Toilet"

    # Collecting the price
    price_raw = soup_html.find("div", class_="price").text.strip()[:-2]
    decimals = float(soup_html.find("div", class_="price").text.strip()[-2:])
    price_sin_decimal = int(locale.atof(price_raw.strip("$")))
    price_clean = price_sin_decimal + (decimals/100)

    # Collecting the sku
    sku_ref_bar = soup_html.find_all("h2", class_="product-info-bar__detail--7va8o")

    # Initializing the SKU
    sku_ref = ""
    for item_raw in sku_ref_bar:
        item = item_raw.text.strip().split(" #")[0]
        if item == "Internet":
            sku_ref = item_raw.text.strip().split(" #")[1]


    # Collecting the image
    image_raw = soup_html.find("a", class_="mediagallery__anchor")
    image_html = image_raw.find("img")
    url_img = image_html["src"]

    # ------------------------------------------------------------------------------------------------------------------
    # Message display
    print("Recopilando la información de {}".format(url_link))
    print("La marca es la: {}".format(brand_name))
    print("El sanitario es el: {}".format(product_name))
    print("El tipo de producto es un: {}".format(product_format))
    print("El sku es el: {}".format(sku_ref))
    print("El precio es: {} USD".format(price_clean))
    print(url_img)
    print("\n")
    # ------------------------------------------------------------------------------------------------------------------

    # Appending the item in a list
    information = [datetime.datetime.today().date(), brand_name, product_format, brand_name, product_name, sku_ref,
                   price_clean, "USD", "homedepot.com", "Si", url_link, url_img]

    return information


# ----------------------------------------------------------------------------------------------------------------------
# Main code
# ----------------------------------------------------------------------------------------------------------------------
for product_type, output_path in [[url_path_toilet, output_path_toilet]]:
    # Reading .csv file with url list
    url_list = pd.read_csv(product_type)

    # Scrapping the information of every url
    data = []
    for url in url_list["URL_product"]:
        # send request to scraperapi, and automatically retry failed requests
        params = {'api_key': API_KEY, 'url': url}

        for i in range(NUM_RETRIES):
            # Random Wait between request
            delay = np.random.choice(delays)
            time.sleep(delay)
            try:
                response = requests.get('http://api.scraperapi.com/', params=urlencode(params))
                # response = requests.get(url, proxies=proxies, headers=headers)

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
            # Parse data with beautifulsoup
            soup: BeautifulSoup = BeautifulSoup(response.content, "html.parser")

            # Getting the information from the website
            toilet_information = homedepot_data(url, soup)
            data.append(toilet_information)

    # Creating the dataframe
    df = pd.DataFrame(data, columns=["Fecha", "Marca", "Tipo", "Familia", "Producto", "SKU", "Precio", "Moneda",
                                     "Market_Place", "Stock", "URL", "Image_url"])

    # Saving the file in a .csv file
    df.to_csv(output_path, mode='a', header=not os.path.exists(output_path), index=False)
