# Python project for URL collection
# Creado por: Juan Monsalvo

# ----------------------------------------------------------------------------------------------------------------------
# Libraries import
# ----------------------------------------------------------------------------------------------------------------------
import pandas as pd
import requests

from bs4 import BeautifulSoup

# ----------------------------------------------------------------------------------------------------------------------
# Configuration and Global Variables
# ----------------------------------------------------------------------------------------------------------------------

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

# Scrapping the URL direction of the listing items
URL_toilet = []
URL_img = []
for toilets_element in toilets_elements:
    product = toilets_element.find("a", class_="product-image")
    URL_toilet.append(product["href"])
    URL_img.append(product.find("img")['src'])

# Dataframe creation
df_url = pd.DataFrame(data=URL_toilet, columns=["URL_Toilet"])

# Saving the URL in a .csv file
output_path = './XX_Url/Decorceramica_twopieces_URL.csv'
df_url.to_csv(output_path, index=False)
