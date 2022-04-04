# Python project for pricing scripping of different sites
# Creado por: Juan Monsalvo

# ----------------------------------------------------------------------------------------------------------------------
# Libraries import
# ----------------------------------------------------------------------------------------------------------------------
import datetime
import locale
import os

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
output_path_toilet = './XX_Data/Corona_toilet-' + str(fecha.year) + '_' + str(fecha.month) + '.csv'
output_path_asiento = './XX_Data/Corona_asiento-' + str(fecha.year) + '_' + str(fecha.month) + '.csv'

# Path for loading the URL sites
url_path_toilet = './XX_Url/Corona_toilets_URL.csv'
url_path_asiento = './XX_Url/Corona_asientos_URL.csv'
# ----------------------------------------------------------------------------------------------------------------------
# Function Definition
# ----------------------------------------------------------------------------------------------------------------------
def corona_data(url, soup_html):
    """
    Programa que toma la información general de una pagina de producto del market place de corona
    """
    # Collecting the name and product tipe
    product_name = soup_html.find("div", class_="name").text.strip()
    tipo_ref = product_name.split(' ', 1)[0]
    product_ref = product_name.split(' ', 1)[1]

    # Collecting the sku
    sku_ref = soup_html.find("div", class_="sku").text.strip().split()[-1]

    # Collecting the price
    price_raw = soup_html.find("span", class_="price").text.strip()
    price_IVA = int(locale.atof(price_raw.strip("$")))
    if price_raw == "":
        price_IVA = 0
    else:
        # Correcting the price
        price_IVA = int(locale.atof(price_raw.strip("$")))

    # Collecting the stock
    stock_flag = soup_html.find("div", class_="coc-productsold-form-wp coc-productsold-component")
    if stock_flag is None:
        stock = "Si"
    else:
        stock = "No"

    # Collecting the family of the product
    if tipo_ref == "Asiento":
        familia = url.split("/")[-3].split("-", 2)[1].capitalize()
        if familia == "Institucional":
            familia_raw = url.split("/")[-3].split("-")[1:3]
            familia = " ".join(familia_raw).capitalize()
    else:
        familia = url.split("/")[-3].split("-", 1)[1].replace("-", " ").capitalize()

    # Collecting the image
    image_html = soup_html.find("img", class_="owl-lazy")
    URL_img = "https://corona.co" + image_html["data-src"]

    # ------------------------------------------------------------------------------------------------------------------
    # Message display
    print("Recopilando la información de {}".format(url))
    # print("El sanitario es el: {}".format(product_ref))
    # print("El sku es el: {}".format(sku_ref))
    # print("El precio es: {}".format(price_IVA))
    # print(URL_img)
    # print("\n")
    # ------------------------------------------------------------------------------------------------------------------

    # Appending the item in a list
    information = [datetime.datetime.today().date(), "Corona", tipo_ref, familia, product_ref, sku_ref,
                   price_IVA, "COP", "corona.co", stock, url, URL_img]

    return information


# ----------------------------------------------------------------------------------------------------------------------
# Main code
# ----------------------------------------------------------------------------------------------------------------------
for product_type, output_path in [[url_path_toilet, output_path_toilet], [url_path_asiento, output_path_asiento]]:
    # Reading .csv file with url list
    url_list = pd.read_csv(product_type)

    # Scrapping the information of every url
    data = []
    for url in url_list["URL_product"]:
        # Surfing the different URL
        result = requests.get(url)
        soup = BeautifulSoup(result.content, "html.parser")

        # Getting the information from the website
        toilet_information = corona_data(url, soup)
        data.append(toilet_information)

        # Getting the variations from each toilet
        # print(url)
        product_variant = soup.find("div", class_="coc-variant-section")
        if product_variant is not None:
            # print("El producto tiene variaciones")
            # --------------------------------------------------------------------------------------------------------------
            # --------------------------------------------------------------------------------------------------------------
            # Color variation
            color_variation = product_variant.find("div", class_="coc-variant-selector coc-variant-type--image")
            if color_variation is not None:
                # print("El producto tiene variaciones de color")
                # Getting all the color variation
                colors = color_variation.find_all("li", class_="coc-variant-option")

                # Getting the data for all the colors
                for item in colors:
                    color = item.find("a", class_="coc-variant-swatch")
                    color_URL = "https://corona.co" + color["href"]

                    if color_URL != url and len(color_URL.split("/")[-1]) < 12:
                        # print(color_URL)
                        # Surfing the different URL
                        result_color = requests.get(color_URL)
                        soup_color = BeautifulSoup(result_color.content, "html.parser")

                        # Getting the information from the website
                        toilet_information = corona_data(color_URL, soup_color)
                        data.append(toilet_information)
            # --------------------------------------------------------------------------------------------------------------
            # --------------------------------------------------------------------------------------------------------------
            # Form variation
            forma_variation = product_variant.find("div", class_="coc-variant-selector coc-variant-type--text")
            if forma_variation is not None:
                # Checking for more than one variation
                forma_size = len(forma_variation.find_all("li", class_="coc-variant-option"))
                if forma_size > 1:
                    # print("El producto tiene variaciones de forma")
                    forma = forma_variation.find("li", class_="coc-variant-option").find("a", class_="coc-variant-swatch")
                    forma_URL = "https://corona.co" + forma["href"]

                    # Form variation URL
                    result_forma = requests.get(forma_URL)
                    soup_forma = BeautifulSoup(result_forma.content, "html.parser")

                    # Check for variation in color
                    color_variation = soup_forma.find("div", class_="coc-variant-selector coc-variant-type--image")

                    if color_variation is not None:
                        # Getting all the color variation
                        colors = color_variation.find_all("li", class_="coc-variant-option")

                        # Getting the data for all the colors
                        for item in colors:
                            color = item.find("a", class_="coc-variant-swatch")
                            color_URL = "https://corona.co" + color["href"]

                            # print(color_URL)
                            # Surfing the different URL
                            result_color = requests.get(color_URL)
                            soup_color = BeautifulSoup(result_color.content, "html.parser")

                            # Getting the information from the web site
                            toilet_information = corona_data(color_URL, soup_color)
                            data.append(toilet_information)
                    else:
                        # print(forma_URL)
                        # Getting the information from the web site
                        toilet_information = corona_data(forma_URL, soup_forma)
                        data.append(toilet_information)


    # Creating the dataframe
    df = pd.DataFrame(data, columns=["Fecha", "Marca", "Tipo", "Familia", "Producto", "SKU", "Precio", "Moneda",
                                     "Market_Place", "Stock", "URL", "Image_url"])


    # Saving the file in a .csv file
    df.to_csv(output_path, mode='a', header=not os.path.exists(output_path), index=False)
