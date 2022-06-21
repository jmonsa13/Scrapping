# Python project for pricing scripping of different sites
# Creado por: Camilo Pardo Macea

# FOR Build
# ----------------------------------------------------------------------------------------------------------------------
# Libraries import
# ----------------------------------------------------------------------------------------------------------------------
import datetime
import os
import time
from urllib.parse import urlencode

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

# ----------------------------------------------------------------------------------------------------------------------
# Configuration and Global Variables
# ----------------------------------------------------------------------------------------------------------------------
# Path definition of the .csv file
fecha = datetime.datetime.today()
output_path_toilet = './XX_Data/Build_toilet-' + str(fecha.year) + '_' + str(fecha.month) + '.csv'

# Path for loading the URL sites
url_path_toilet = './XX_Url/Build_URL.xlsx'

# Number of retry
NUM_RETRIES = 5

# Tell scraper to use Scraper API as the proxy
API_KEY = 'd9d061ea3ad19b7f0eb56c83f416ba06'

# Waiting time between request
delays = [1, 4, 8, 2, 5, 3]

# Header for beautiful soup
headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}


# Function for data extract informacion of product

def build_data(elem, soup_html):
    """
    Programa que toma la información general de una pagina de producto del market place de Build
    """
    # Collecting the name and product type
    brand_name = soup_html.find('h1', class_='ma0 fw6 lh-title di f5 f3-ns').find('span').text
    product_name = soup_html.find('h1', class_='ma0 fw6 lh-title di f5 f3-ns').find('span', class_='fw2 di-ns').text

    if "bowl only" in product_name.lower():
        product_format = "Bowl"
    elif "tank only" in product_name.lower():
        product_format = "Tank"
    else:
        product_format = "Toilet"

    # Collecting the sku
    sku_ref = soup_html.find('h2', class_='f7 fw4 mt1 lh-title theme-grey-medium mt2 mt0-ns '
                                  'mb0').find('span', class_='b').text
    internet_ref = soup_html.find('div', class_='w-25 tr f6').text.split(' ')[2]

    # Collecting the current price
    price_clean = soup_html.find('div', class_='flex flex-row flex-nowrap justify-start mr4 f4 '
                                 'f3-ns pt2-ns').find('span', class_='b lh-copy').text.strip('$')
    # Collecting the image
    url_img = soup_html.find('meta', {'property': 'og:image'}).attrs['content']

    #model = soup_html.find('h2', class_ = 'f7 fw4 mt1 lh-title theme-grey-medium mt2 mt0-ns mb0').find('span', class_='b').text
    #stock = soup_html.find('div', class_ = 'pl1 dib-ns').find('span', class_ = 'theme-accent lh-solid').text.split(' ')[0]
    # ------------------------------------------------------------------------------------------------------------------
    # Message display
    print("Recopilando la información de {}".format(elem["Link"]))
    print("La marca es la: {}".format(brand_name))
    print("El sanitario es el: {}".format(product_name))
    print("El tipo de producto es un: {}".format(product_format))
    print("El sku es el: {}".format(sku_ref))
    print("El sku_internet es el: {}".format(internet_ref))
    print("El precio es: {} USD".format(price_clean))
    print(url_img)
    print("\n")
    # ------------------------------------------------------------------------------------------------------------------
    # Appending the item in a list
    information = [datetime.datetime.today().date(), elem["Fabricante"], elem["Sku"],
                   elem["Linea"], product_format, elem["Rough in"], elem["Bowl Height"], elem["Asiento"],
                   elem["Capacidad (Gpl)"], product_name, internet_ref,
                   price_clean, "USD", "build.com", "Si", elem["Link"], url_img]

    return information


# ----------------------------------------------------------------------------------------------------------------------
# Main code
# ----------------------------------------------------------------------------------------------------------------------
for product_type, output_path in [[url_path_toilet, output_path_toilet]]:
    # Reading .xlsx file with url list
    file_df = pd.read_excel(product_type)

    # Keeping just the row with links
    product_df = file_df[file_df['Link'].notna()]

    # Scrapping the information of every url
    data = []
    for index, elem in product_df.iterrows():
        # send request to scraperapi, and automatically retry failed requests
        params = {'api_key': API_KEY, 'url': elem["Link"]}

        for i in range(NUM_RETRIES):
            # Random Wait between request
            delay = np.random.choice(delays)
            time.sleep(delay)
            try:
                response = requests.get('http://api.scraperapi.com/', params=urlencode(params))
                #response = requests.get(elem["Link"], headers=headers)

                print("Intento numero {}".format(i))
                print(response)
                if response.status_code in [200, 404]:
                    # escape for loop if the API returns a successful response
                    break
            except requests.exceptions.ConnectionError:
                response = ''
                print("ConnectionError")
        try:
            estate = response.status_code
        except:
            estate = 900

        # parse data if 200 status code (successful response)
        if estate == 200:
            # Parse data with beautifulsoup
            soup: BeautifulSoup = BeautifulSoup(response.content, "html.parser")

            # Getting the information from the website
            toilet_information = build_data(elem, soup)
            data.append(toilet_information)

    # Creating the dataframe
    df = pd.DataFrame(data, columns=["Fecha", "Fabricante", "SKU", "Linea", "Tipo", "Rough_In",
                                     "Bowl Height", "Asiento", "Capacidad (Gpl)", "Producto",
                                     "Cod_Internet", "Precio", "Moneda",
                                     "Market_Place", "Stock", "URL", "Image_url"])

    # Saving the file in a .csv file
    df.to_csv(output_path, mode='a', header=not os.path.exists(output_path), index=False)

