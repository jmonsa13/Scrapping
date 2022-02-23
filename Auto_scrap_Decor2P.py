# Python project for pricing scripping of different sites
# Creado por: Juan Monsalvo

# ----------------------------------------------------------------------------------------------------------------------
# Libraries import
# ----------------------------------------------------------------------------------------------------------------------
import datetime
import locale
import os

import numpy as np
import pandas as pd
import requests

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
output_path = './XX_Data/Decorceramica_twopieces-' + str(fecha.year) + '_' + str(fecha.month) + '.csv'

# Path for loading the URL sites
url_path = './XX_Url/Decorceramica_twopieces_URL.csv'

# ----------------------------------------------------------------------------------------------------------------------
# Main code
# ----------------------------------------------------------------------------------------------------------------------
# Reading .csv file with url list
URL_toilet = pd.read_csv(url_path)

# Scrapping the information of every url
data = []
for url in URL_toilet["URL_Toilet"]:
    # Surfing the different URL
    result = requests.get(url)
    soup = BeautifulSoup(result.content, "html.parser")

    # Collecting the data of each URL
    product_ref = soup.find("h2", class_="det-title").text.strip()
    sku_ref = soup.find("div", class_="skuReference").text.strip()
    price_ref = soup.find("strong",
                          class_="skuBestPrice").text.strip()  # OJO el precio que se muestra aqui esta sin iva

    # Collecting the image
    image_html = soup.find("a", class_="image-zoom")
    URL_img = image_html["href"]

    # If there is not stock of the product
    if price_ref == "":
        price_IVA = 0  # Price is defined as 0
    else:
        # Correcting the price
        raw_numbers = locale.atof(price_ref.strip("$"))
        price_IVA = int(np.round(raw_numbers * 1.19))

    # Message display
    print("Recopilando la información de {}".format(url))
    # print("El sanitario es el: {}".format(product_ref))
    # print("El sku es el: {}".format(sku_ref))
    # print("El precio es: {}".format(price_IVA))
    # print(URL_img)
    # print("\n")

    # Appending the item in a list
    data.append([datetime.datetime.today().date(), "Decorceramica", product_ref, sku_ref, price_IVA, url, URL_img])

# Creating the dataframe
df = pd.DataFrame(data, columns=["Fecha", "Marca", "Producto", "SKU", "Precio", "URL", "Image_url"])

# Saving the file in a .csv file
df.to_csv(output_path, mode='a', header=not os.path.exists(output_path), index=False)


