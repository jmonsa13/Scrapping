# Python project for pricing scripping of different sites
# Creado por: Juan Felipe Monsalvo Salazar

# FOR Afsupply
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
folder = fecha.strftime('%Y-%m')
if not os.path.exists('./XX_Data/' + folder):
    os.makedirs('./XX_Data/' + folder)
output_path_toilet = './XX_Data/' + folder + '/Afsupply_toilet-' + str(fecha.year) + '_' + str(fecha.month) + '.csv'

# Path for loading the URL sites
url_path_toilet = './XX_Url/Afsupply.xlsx'

# Number of retry
NUM_RETRIES = 5

# Tell scraper to use Scraper API as the proxy
# API_KEY = '9c2caae056c046ad7fed2af9eeda0100'  # hotmail.com
API_KEY = '48f0187b8c701cbe3479abbf6e6f9d81'  # gmail.com


# Waiting time between request
delays = [1, 4, 8, 2, 5, 3]

# Header for beautiful soup
headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}


# Function for data extract informacion of product
def afsupply_data(elem, soup_html):
    """
    Programa que toma la información general de una pagina de producto del market place de Afsupply
    """
    # Collecting the name and product type
    brand_name = elem["Fabricante"]
    product_name = elem["Short Name"]
    product_format = elem["Type"]
    # brand_name = soup_html.find('div', class_='product-detail__brand-container').text.strip()
    # product_name = soup_html.find('div', class_='page-title-wrapper product').find('h1').text.strip()

    # Collecting the sku
    # sku_ref = soup_html.find('div', class_='product-number').find('span', class_='itemNumber').text
    internet_ref = soup_html.find('div', class_='product-info-stock-sku')\
        .find('div', class_='value').text.strip()

    # Collecting the current price
    price_old = float(soup_html.find('span', class_='old-price')
                      .find('span', class_='price').text.strip().strip("$"))
    price_clean = float(soup_html.find('span', class_='special-price')
                        .find('span', class_='price').text.strip().strip("$"))

    # Collecting the image
    url_img = soup_html.find('div', class_='product media')\
        .find('div', class_='gallery-placeholder _block-content-loading').find('img')["src"]

    # Stock Online
    stock_flag = soup_html.find('div', class_='product-info-price').find('p').find('span')
    if stock_flag is None:
        stock = 'No'
    else:
        if stock_flag.text.strip() == 'In Stock.':
            stock = 'Si'
    # ------------------------------------------------------------------------------------------------------------------
    # Message display
    print("Recopilando la información de {}".format(elem["Link"]))
    # print("La marca es la: {}".format(brand_name))
    print("El sanitario es el: {}".format(product_name))
    print("El tipo de producto es un: {}".format(product_format))
    # print("El sku es el: {}".format(sku_ref))
    print("El sku_internet es el: {}".format(internet_ref))
    print("El precio listado es: {} USD".format(price_clean))
    print(url_img)
    print("\n")
    # ------------------------------------------------------------------------------------------------------------------
    # Appending the item in a list
    information = [datetime.datetime.today().date(), brand_name, elem["Sku"],
                   elem["Linea"], product_format, elem["Rough in"], elem["Bowl Height"], elem["Asiento"],
                   elem["Capacidad (Gpl)"], product_name, internet_ref,
                   price_clean, "USD", "afsupply.com", stock, elem["Link"], url_img]

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
                # response = requests.get(elem["Link"], headers=headers)

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
            toilet_information = afsupply_data(elem, soup)
            data.append(toilet_information)

    # Creating the dataframe
    df = pd.DataFrame(data, columns=["Fecha", "Fabricante", "SKU", "Linea", "Tipo", "Rough_In",
                                     "Bowl Height", "Asiento", "Capacidad (Gpl)", "Producto",
                                     "Cod_Internet", "Precio", "Moneda",
                                     "Market_Place", "Stock", "URL", "Image_url"])

    # Saving the file in a .csv file
    df.to_csv(output_path, mode='a', header=not os.path.exists(output_path), index=False)