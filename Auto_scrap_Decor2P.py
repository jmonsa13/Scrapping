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
output_path = './Data/Decorceramica_twopieces-' + str(fecha.year) + '_' + str(fecha.month) + '.csv'

# ----------------------------------------------------------------------------------------------------------------------
# Main code
# ----------------------------------------------------------------------------------------------------------------------
# URL definitioin
URL = "https://www.decorceramica.com/busca/?fq=C:15/16&fq=spec_fct_243:1%20Pieza?O=OrderByScoreDESC"
page = requests.get(URL)

# Charging the content of the page using beautifulsoup
soup = BeautifulSoup(page.content, "html.parser")
# print(soup.prettify())

# Finding the id and items where the products are located
results = soup.find(id="collections")
toilets_elements = results.find_all("div", class_="item")

# Scrapping the names and prices of every item
data = []
for elem in toilets_elements:
    product_ref = elem.find("b", class_="product-name").text.strip()
    try:
        elem.find("span", class_="out-of-stock").text.strip()
        if elem.find("span", class_="out-of-stock").text.strip() == "Disponible próximamente":
            price_ref = elem.find("span", class_="out-of-stock").text.strip()

            message_price = "El producto no tiene existencia actualmente."
            message_priceIVA = " "
            price_IVA = 0
    except:
        price_ref = elem.find("span",
                              class_="best-price").text.strip()  # OJO el precio que se muestra aqui esta sin iva
        raw_numbers = locale.atof(price_ref.strip("$"))

        message_price = "El precio sin IVA es de: {}".format(price_ref)
        message_priceIVA = "El precio con IVA es de: ${}".format(int(np.round(raw_numbers * 1.19)))
        price_IVA = int(np.round(raw_numbers * 1.19))

    # print("El sanitario es el: {}".format(product_ref))
    # print(message_price)
    # print(message_priceIVA)

    # Appending the item in a list
    data.append([datetime.datetime.today().date(), product_ref, price_IVA])

# Creating the dataframe
df = pd.DataFrame(data, columns=["Date", "Product", "Price"])

# Saving the file in a .csv file
df.to_csv(output_path, mode='a', header=not os.path.exists(output_path), index=False)


