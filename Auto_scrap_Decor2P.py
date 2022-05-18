# Python project for pricing scripping of different sites
# Creado por: Juan Monsalvo

# ----------------------------------------------------------------------------------------------------------------------
# Libraries import
# ----------------------------------------------------------------------------------------------------------------------
import datetime
import os

import numpy as np
import pandas as pd
import requests

from bs4 import BeautifulSoup

# ----------------------------------------------------------------------------------------------------------------------
# Configuration and Global Variables
# ----------------------------------------------------------------------------------------------------------------------
# Path definition of the .csv file
fecha = datetime.datetime.today()
output_path = './XX_Data/Decorceramica_twopieces-' + str(fecha.year) + '_' + str(fecha.month) + '.csv'

# Path for loading the URL sites
url_path = './XX_Url/Decorceramica_twopieces_URL.csv'

# Text to remove from the family
aux = ["ELONGADO", "BLANCO", "REDONDO", "BEIGE", "NEGRO", "SPRAY", "VERTICAL", "ELONG", "1", "PZ"]
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

    # Collecting the name
    product_ref_raw = soup.find("h2", class_="det-title").text.strip()
    product_ref = product_ref_raw.split(" ", 1)[1]

    # Collecting the type of product
    tipo = product_ref_raw.split(" ", 1)[0]

    # Collecting the family name
    new = []
    for j in product_ref.split(" "):
        if j not in aux:
            new.append(j)
    familia = " ".join(new)

    # Collecting the sku
    sku_ref = soup.find("div", class_="skuReference").text.strip()

    # Collecting the price
    price_ref = soup.find("strong",
                          class_="skuBestPrice").text.strip()  # OJO el precio que se muestra aqui esta sin iva

    # If there is not stock of the product
    if price_ref == "":
        price_IVA = 0  # Price is defined as 0
        stock = "No"
    else:
        # Correcting the price
        raw_numbers = float(price_ref.strip("$").replace(".", "").replace(",", "."))
        price_IVA = int(np.round(raw_numbers * 1.19))
        stock = "Si"

    # Collecting the image
    image_html = soup.find("a", class_="image-zoom")
    URL_img = image_html["href"]

    # Message display
    print("Recopilando la información de {}".format(url))
    # print("El sanitario es el: {}".format(product_ref))
    # print("El sku es el: {}".format(sku_ref))
    # print("El precio es: {}".format(price_IVA))
    # print(URL_img)
    # print("\n")

    # Appending the item in a list
    data.append([datetime.datetime.today().date(), "Decorceramica", tipo, familia, product_ref, sku_ref, price_IVA,
                 "COP", "decorceramica.com", stock, url, URL_img])

# Creating the dataframe
df = pd.DataFrame(data, columns=["Fecha", "Marca", "Tipo", "Familia", "Producto", "SKU", "Precio", "Moneda",
                                 "Market_Place", "Stock", "URL", "Image_url"])
# Saving the file in a .csv file
df.to_csv(output_path, mode='a', header=not os.path.exists(output_path), index=False)


