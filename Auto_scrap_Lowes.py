# Python project for pricing scripping of different sites
# Creado por: Juan Monsalvo

# FOR Lowes
# ----------------------------------------------------------------------------------------------------------------------
# Libraries import
# ----------------------------------------------------------------------------------------------------------------------
import datetime
import json
import os
import re
import time
from urllib.parse import urlencode

import numpy as np
import pandas as pd
import requests

# ----------------------------------------------------------------------------------------------------------------------
# Configuration and Global Variables
# ----------------------------------------------------------------------------------------------------------------------
# Header for beautiful soup
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0"
}
cookies = {"sn":"3256", "region":"east"}

# Path definition of the .csv file
fecha = datetime.datetime.today()
output_path_toilet = './XX_Data/Lowes_toilet-' + str(fecha.year) + '_' + str(fecha.month) + '.csv'

# Path for loading the URL sites
url_path_toilet = './XX_Url/Lowes.xlsx'

# Number of retry
NUM_RETRIES = 5

# Tell scraper to use Scraper API as the proxy
API_KEY = 'd9d061ea3ad19b7f0eb56c83f416ba06'

# Waiting time between request
delays = [1, 4, 8, 2, 5, 3]


# ----------------------------------------------------------------------------------------------------------------------
# Function Definition
# ----------------------------------------------------------------------------------------------------------------------
def lowes_data(elem, data):
    """
    Programa que toma la información general de una pagina de producto del market place de Ferguson
    """

    item_id = elem['Link'].split("/")[-1]
    # print(json.dumps(data["productDetails"][item_id], indent=4, sort_keys=True))

    # Collecting the name and product tipe
    Status = data["productDetails"][item_id]["product"]["status"]
    brand_name = data["productDetails"][item_id]["product"]["brand"]
    product_name = data["productDetails"][item_id]["product"]["description"]

    if "toilet" in product_name.lower():
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
    try:
        price_clean = float(data["productDetails"][item_id]["price"]["analyticsData"]["sellingPrice"])
    except:
        price_clean = ""

    try:
        was_price_clean = float(data["productDetails"][item_id]["price"]["analyticsData"]["wasPrice"])
    except:
        was_price_clean = ""

    try:
        offert_price = float(data["productDetails"][item_id]["offerPromotions"]["offerPrice"])
    except:
        offert_price = ""

    # print("PromoMsg:", data["productDetails"][item_id]["offerPromotions"]["displayPromoMsg"])
    # print("Currency:", data["productDetails"][item_id]["price"]["newPrice"]["price"]["currency"])

    # Collecting the sku of product
    sku_ref = data["productDetails"][item_id]["product"]["omniItemId"]
    item_ref = data["productDetails"][item_id]["product"]["itemNumber"]
    model_ref = data["productDetails"][item_id]["product"]["modelId"]

    # Collecting the image
    aux_url_img = data["productDetails"][item_id]["product"]["imageUrls"][0]["value"]
    url_img = 'https://mobileimages.lowes.com' + aux_url_img

    # Stock
    try:
        aux_stock = int(data["productDetails"][item_id]["itemInventory"]["totalAvailableQty"])
        if aux_stock >= 0:
            stock = "Si"
        else:
            stock = "No"
    except:
        stock = "No Disponible"
    # ------------------------------------------------------------------------------------------------------------------
    # Message display
    print("Recopilando la información de {}".format(elem["Link"]))
    print("La marca es la: {}".format(brand_name))
    print("El sanitario es el: {}".format(product_name))
    print("El tipo de producto es un: {}".format(product_format))
    print("El sku es el: {}".format(sku_ref))
    print("El item es el: {}".format(item_ref))
    print("El model es el: {}".format(model_ref))
    print("El precio actual es: {} USD".format(price_clean))
    print("El precio anterior es: {} USD".format(was_price_clean))
    print("El precio con descuento especial es: {} USD".format(offert_price))
    print("Inventario:{}".format(stock))
    print(url_img)
    print("\n")
    # ------------------------------------------------------------------------------------------------------------------

    # Appending the item in a list
    information = [datetime.datetime.today().date(), elem["Fabricante"], elem["Sku"],
                   elem["Linea"], product_format, elem["Rough in"], elem["Bowl Height"], elem["Asiento"],
                   elem["Capacidad (Gpl)"], product_name, item_ref,
                   price_clean, "USD", "lowes.com", "Si", elem["Link"], url_img]

    return information


# ----------------------------------------------------------------------------------------------------------------------
# Main code
# ----------------------------------------------------------------------------------------------------------------------
# Scrapping the information of every url
for product_type, output_path in [[url_path_toilet, output_path_toilet]]:
    # Reading .xlsx file with url list
    file_df = pd.read_excel(product_type)

    # Keeping just the row with links
    product_df = file_df[file_df['Link'].notna()]

    # Scrapping the information of every product
    datos = []
    for index, elem in product_df.iterrows():
        # send request to scraperapi, and automatically retry failed requests
        params = {'api_key': API_KEY, 'url': elem["Link"], "country_code": "us"}

        for i in range(NUM_RETRIES):
            # Random Wait between request
            delay = np.random.choice(delays)
            time.sleep(delay)
            try:
                response = requests.get('http://api.scraperapi.com/', params=urlencode(params))
                # response = requests.get(elem["Link"], headers=headers, cookies=cookies)

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
            # Parse data with json
            t = response.text
            data = re.search(r"window\['__PRELOADED_STATE__'\] = (\{.*?\})<", t)
            data = json.loads(data.group(1))

            # Uncomment to print all data:
            # print(json.dumps(data, indent=4))

            # Getting the information from the website
            toilet_information = lowes_data(elem, data)
            datos.append(toilet_information)

    # Creating the dataframe
    df = pd.DataFrame(data, columns=["Fecha", "Fabricante", "SKU", "Linea", "Tipo", "Rough_In",
                                     "Bowl Height", "Asiento", "Capacidad (Gpl)", "Producto",
                                     "Cod_Internet", "Precio", "Moneda",
                                     "Market_Place", "Stock", "URL", "Image_url"])

    # Saving the file in a .csv file
    df.to_csv(output_path, mode='a', header=not os.path.exists(output_path), index=False)