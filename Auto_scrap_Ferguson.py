# Python project for pricing scripping of different sites
# Creado por: Juan Monsalvo

# FOR Ferguson
# ----------------------------------------------------------------------------------------------------------------------
# Libraries import
# ----------------------------------------------------------------------------------------------------------------------
import datetime
import os
import time

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

# ----------------------------------------------------------------------------------------------------------------------
# Configuration and Global Variables
# ----------------------------------------------------------------------------------------------------------------------
# Path definition of the .csv file
fecha = datetime.datetime.today()
# Checking and creating the folder
folder = fecha.strftime('%Y-%m')
if not os.path.exists('./XX_Data/' + folder):
    os.makedirs('./XX_Data/' + folder)
output_path_toilet = './XX_Data/' + folder + '/Ferguson_toilet-' + str(fecha.year) + '_' + str(fecha.month) + '.csv'

# Path for loading the URL sites
url_path_toilet = './XX_Url/Ferguson_URL.xlsx'

# Number of retry
NUM_RETRIES = 5

# Waiting time between request
delays = [1, 4, 8, 2, 5, 3]

# Header for beautiful soup
headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}


# ----------------------------------------------------------------------------------------------------------------------
# Function Definition
# ----------------------------------------------------------------------------------------------------------------------
def ferguson_data(elem, soup_html):
    """
    Programa que toma la información general de una pagina de producto del market place de Ferguson
    """

    # Collecting the name and product tipe
    brand_name = soup.find("h2", class_="product__brand").text.strip()
    product_name = soup.find("h1", class_="product__name").text.strip()

    if "two piece" in product_name.lower():
        product_format = "Toilet"
    elif "one piece" in product_name.lower():
        product_format = "One Piece"
    elif "bowl" in product_name.lower():
        product_format = "Bowl"
    elif "tank" in product_name.lower():
        product_format = "Tank"
    else:
        product_format = ""

    # Collecting the price
    price_clean = float(soup.find("span", class_="price__main price-value").text.strip())

    # TODO: Capturar en promoción

    # Collecting the sku of product
    sku_ref_bar = soup.find("span", class_="customer-code")
    sku_ref = sku_ref_bar.text.strip().split(" #")[1]

    # Collecting the sku of internet
    item_ref = ""
    ref_info = soup.find("p", class_="product__prop")
    for item_raw in ref_info.find_all("span"):
        item = item_raw.text.strip().split(" #")[0].strip("|").strip()
        if item == "Item":
            item_ref = item_raw.text.strip().split(" #")[1]

    # Todo: Tomar dato de envio
    # Taking delivery cost
    # delivery = soup_html.find("div", class_="buybox__car")
    # print(delivery)

    # Collecting the image
    url_img = soup.find("a", class_="active")["data-image"]
    # ------------------------------------------------------------------------------------------------------------------
    # Message display
    print("Recopilando la información de {}".format(elem["Link"]))
    print("La marca es la: {}".format(brand_name))
    print("El sanitario es el: {}".format(product_name))
    print("El tipo de producto es un: {}".format(product_format))
    print("El sku es el: {}".format(sku_ref))
    print("El precio actual es: {} USD".format(price_clean))
    #print("El precio anterior es: {} USD".format(was_price_clean))
    print(url_img)
    print("\n")
    # ------------------------------------------------------------------------------------------------------------------

    # Appending the item in a list
    information = [datetime.datetime.today().date(), elem["Fabricante"], elem["Sku"],
                   elem["Linea"], product_format, elem["Rough in"], elem["Bowl Height"], elem["Asiento"],
                   elem["Capacidad (Gpl)"], product_name, item_ref,
                   price_clean, "USD", "ferguson.com", "Si", elem["Link"], url_img]

    return information


# ----------------------------------------------------------------------------------------------------------------------
# Main code
# ----------------------------------------------------------------------------------------------------------------------
for product_type, output_path in [[url_path_toilet, output_path_toilet]]:
    # Reading .xlsx file with url list
    file_df = pd.read_excel(product_type)

    # Keeping just the row with links
    product_df = file_df[file_df['Link'].notna()]

    # Scrapping the information of every product
    data = []
    for index, elem in product_df.iterrows():
        for i in range(NUM_RETRIES):
            # Random Wait between request
            delay = np.random.choice(delays)
            time.sleep(delay)
            try:
                response = requests.get(elem["Link"], headers=headers)

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
            toilet_information = ferguson_data(elem, soup)
            data.append(toilet_information)

    # Creating the dataframe
    df = pd.DataFrame(data, columns=["Fecha", "Fabricante", "SKU", "Linea", "Tipo", "Rough_In",
                                     "Bowl Height", "Asiento", "Capacidad (Gpl)", "Producto",
                                     "Cod_Internet", "Precio", "Moneda",
                                     "Market_Place", "Stock", "URL", "Image_url"])

    # Saving the file in a .csv file
    df.to_csv(output_path, mode='a', header=not os.path.exists(output_path), index=False)
