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
toilet_url = "https://corona.co/productos/sanitarios/sanitarios-individuales/c/sanitarios-individuales?q=%3Aprice-" \
             "desc&page={}"
asientos_url = "https://corona.co/productos/asientos-sanitarios/c/asientos-sanitarios?q=%3Arelevance&page={}"


# ----------------------------------------------------------------------------------------------------------------------
# Function Definition
# ----------------------------------------------------------------------------------------------------------------------
def url_list(web_url):
    """
    Function to recover all the url from the grid of product from corona website
    :param web_url:
    :return: df_url
    """
    # Initialization variable
    url_product = []

    # Scrapping all the pages of the URL
    for pag in range(10):
        # Charging the content of the page using beautifulsoup
        url = web_url.format(pag)
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")

        # Finding the id and items where the products are located
        results = soup.find("div", class_="product__listing product__grid")
        elements = results.find_all("div", class_="details")

        # Scrapping the URL direction of the listing items
        for element in elements:
            product = element.find("a", class_="reference")
            url_product.append("https://corona.co" + product["href"])

    # Dataframe creation
    df_url = pd.DataFrame(data=url_product, columns=["URL_product"])

    return df_url


# ----------------------------------------------------------------------------------------------------------------------
# Main code
# ----------------------------------------------------------------------------------------------------------------------
# URL file creation toilets
df = url_list(toilet_url)

# Saving the URL in a .csv file
df.to_csv('./XX_Url/Corona_toilets_URL.csv', index=False)
# ----------------------------------------------------------------------------------------------------------------------
# URL file creation Asientos
df = url_list(asientos_url)

# Saving the URL in a .csv file
df.to_csv('./XX_Url/Corona_asientos_URL.csv', index=False)
