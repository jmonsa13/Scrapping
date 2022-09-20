# Python project for pricing scripping of different sites
# Creado por: Juan Felipe Monsalvo Salazar

# FOR Mansfield
# ----------------------------------------------------------------------------------------------------------------------
# Libraries import
# ----------------------------------------------------------------------------------------------------------------------
import numpy as np
import datetime
import os

import pandas as pd

# ----------------------------------------------------------------------------------------------------------------------
# Configuration and Global Variables
# ----------------------------------------------------------------------------------------------------------------------
# Path definition of the .csv file
fecha = datetime.datetime.today() # Checking and creating the folder
folder = fecha.strftime('%Y-%m')
if not os.path.exists('./XX_Data/' + folder):
    os.makedirs('./XX_Data/' + folder)
output_path_toilet = './XX_Data/' + folder + '/Mansfield_wholesaler-' + str(fecha.year) + '_' + str(fecha.month) + '.csv'

# Path for loading the URL sites
url_path_toilet = './XX_Master_database/Wholesaler_Database.xlsx'
fabricante = 'Mansfield'

# Number of retry
# NUM_RETRIES = 5

# Waiting time between request
# delays = [1, 4, 8, 2, 5, 3]

# Header for beautiful soup
# headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 '
#                          '(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}


# ----------------------------------------------------------------------------------------------------------------------
# Main code
# ----------------------------------------------------------------------------------------------------------------------
for product_type, output_path in [[url_path_toilet, output_path_toilet]]:

    # Reading .xlsx file
    file_df = pd.read_excel(product_type, sheet_name='Mansfield')
    file_df = file_df[file_df['Fabricante'] == fabricante]

    # initialization of the list
    data = []

   # ------------------------------------------------------------------------------------------------------------------
    # Keeping just the row without links
    product_df_notlink = file_df[file_df['Link'].isna()]

    # Scrapping the information for every element
    for index, elem in product_df_notlink.iterrows():
        brand_name = elem["Fabricante"]
        product_name = elem["Description"]
        product_subcategory = elem["Subcategory"]
        product_format = elem["Tipo"]
        linea_name = elem["Linea"]
        price_type = elem["Price Type"]
        multiplier = elem['Multiplicador']
        url_img = elem['URL_Img']

        # ------------------------------------------------------------------------------------------------------------------
        # Message display
        print("Recopilando la información de {}".format(elem["Link"]))
        print("La marca es la: {}".format(brand_name))
        print("El sanitario es el: {}".format(product_name))
        print("El tipo de producto es un: {}".format(product_format))
        print("El sku es el: {}".format(elem["Sku"]))
        print("El precio listado es: {} USD".format(elem['Platinum Price']))
        print(url_img)
        print("\n")

        # Appending the item in a list
        information = [datetime.datetime.today().date(), brand_name, elem["Sku"], linea_name, product_subcategory,
                       product_format, elem["Rough in"], elem["Bowl Height"], elem["Asiento"],
                       elem["Capacidad"], product_name, price_type, multiplier, np.round(elem['Platinum Price'], 2),
                       None, "USD", "mansfieldplumbing.com", None, None, url_img]
        data.append(information)
    # ------------------------------------------------------------------------------------------------------------------

    # Creating the dataframe
    df = pd.DataFrame(data, columns=["Fecha", "Fabricante", "SKU", "Linea", 'Subcategoria', "Tipo", "Rough_In",
                                     "Bowl_Height", "Asiento", "Capacidad_(Gpl)", "Producto",
                                     "Price_Type", "Multiplicador", "Precio_Lista", "Precio_Consumidor", "Moneda",
                                     "Market_Place", "Stock", "URL", "Image_url"])

    # Saving the file in a .csv file
    df.to_csv(output_path, mode='a', header=not os.path.exists(output_path), index=False)
