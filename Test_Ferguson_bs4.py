# Python project for pricing scripping of different sites
# Creado por: Juan Monsalvo

# TEST FOR FERGUSON
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
output_path_toilet = './XX_Data/Ferguson_test-' + str(fecha.year) + '_' + str(fecha.month) + '.csv'
# ----------------------------------------------------------------------------------------------------------------------
# General Variables
url1 = 'https://www.ferguson.com/product/gerber-plumbing-maxwell-128-gpf-elongated-floor-mount-two-piece-' \
       'toilet-bowl-in-white-gg0021975/_/R-4493463'

url2 = 'https://www.ferguson.com/product/gerber-plumbing-maxwell-128-gpf-toilet-tank-with-left-hand-trip-' \
       'lever-in-white-gg0028990/_/R-4239960'

url3 = 'https://www.ferguson.com/product/kohler-highline-elongated-toilet-bowl-in-white-k4304-0/_/R-2392202'

url_list = [url1, url2, url3]

NUM_RETRIES = 5

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
    for i in range(NUM_RETRIES):
        # Random Wait between request
        delay = np.random.choice(delays)
        time.sleep(delay)
        try:
            response = requests.get(url,  headers=headers)

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
        brand_name = soup.find("h2", class_="product__brand").text.strip()
        product_name = soup.find("h1", class_="product__name").text.strip()

        if "two piece" in product_name.lower():
            product_format = "Two Piece"
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

        # Collecting the image
        URL_img = soup.find("a", class_="active")["data-image"]

        # ------------------------------------------------------------------------------------------------------------------
        # Message display
        print("Recopilando la información de {}".format(url))
        print("La marca es la: {}".format(brand_name))
        print("El sanitario es el: {}".format(product_name))
        print("El tipo de producto es el: {}".format(product_format))
        print("El sku de fabrica es el: {}".format(sku_ref))
        print("El sku de internet es el: {}".format(item_ref))
        print("El precio es: {} USD".format(price_clean))
        print(URL_img)
        print("\n")
        # ------------------------------------------------------------------------------------------------------------------
        # Appending the item in a list
        information = [datetime.datetime.today().date(), brand_name, "Sanitario", brand_name, product_name, sku_ref,
                       price_clean, "USD", "ferguson.com", "Si", url, URL_img]

        data.append(information)

    # Creating the dataframe
    df = pd.DataFrame(data, columns=["Fecha", "Marca", "Tipo", "Familia", "Producto", "SKU", "Precio", "Moneda",
                                     "Market_Place", "Stock", "URL", "Image_url"])

# Saving the file in a .csv file
df.to_csv(output_path_toilet, mode='a', header=not os.path.exists(output_path_toilet), index=False)


