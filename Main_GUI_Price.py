# Python project Dashboard for pricing
# Creado por: Juan Monsalvo
# ----------------------------------------------------------------------------------------------------------------------
# Libraries import
# ----------------------------------------------------------------------------------------------------------------------
import os
import urllib.request

import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image
from st_aggrid import AgGrid


# ----------------------------------------------------------------------------------------------------------------------
# Configuration and Global Variables
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
# Function Definition
# ----------------------------------------------------------------------------------------------------------------------
def load_data(folder="./Data", filename="Decorceramica_twopieces.csv"):
    """
    Función que carga el archivo csv guardado al conectar con la base de datos y devuelve un dataframe
    """
    df = pd.read_csv(folder + filename)

    return df


# ----------------------------------------------------------------------------------------------------------------------
# Streamlit Setting
# ----------------------------------------------------------------------------------------------------------------------
st.set_page_config(page_title="Monitoreo de Precios",
                   initial_sidebar_state="collapsed",
                   page_icon="📈",
                   layout="wide")

tabs = ["Sanitarios", "Griferías", "Asientos"]
page = st.sidebar.radio("Paginas", tabs, index=0)
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Initial page
st.title('💲 Monitoreo de Precios - Corona 🤖')

# Loading the files
# Folder path definition
directory = './XX_Data'
files = os.listdir(directory)

# Empty data frame
df = pd.DataFrame()

# Loading the DF of each month in a unique DF
for file in files:
    df = pd.concat([df, load_data(folder=directory + '/', filename=file)])
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
if page == "Sanitarios":
    st.header('Historico de Precios Sanitarios')

    st.subheader('Analisis de precios global')
    # Filtering for Sanitario
    df_toilet = df[df["Tipo"] != "Asiento"]

    # Filtering by marca
    marca_sel = st.selectbox("¿Que marca desea analizar?", df_toilet["Marca"].unique(), 0)
    df_toilet = df_toilet[df_toilet["Marca"] == marca_sel]
    # ------------------------------------------------------------------------------------------------------------------
    # Plotting line plot
    fig = px.line(data_frame=df_toilet, x="Fecha", y="Precio", color="Producto", line_group="Producto",
                  title="Historico Precios Decorceramica Two Pieces",
                  width=1000, height=600,
                  # labels={"I_Valid": "Formatos"},
                  template="seaborn")

    fig.update_layout(modebar_add=["v1hovermode", "toggleSpikeLines"])

    fig.update_xaxes(dtick="d0.5", tickformat="%b %d\n%Y", rangeslider_visible=False)
    fig.update_xaxes(showline=True, linewidth=0.5, linecolor='black')
    fig.update_yaxes(showline=True, linewidth=0.5, linecolor='black')

    # Set x-axis and y-axis title
    fig['layout']['xaxis']['title'] = 'Fechas'
    fig['layout']['yaxis']['title'] = "Precios en COP"

    st.plotly_chart(fig, use_container_width=True)


    with st.expander("Ver datos"):
        AgGrid(df_toilet, editable=False, sortable=True, filter=True, resizable=True, defaultWidth=5,
               fit_columns_on_grid_load=False, theme="streamlit",  # "light", "dark", "blue", "material"
               key="Toilet", reload_data=True,  # gridOptions=gridoptions,
               enable_enterprise_modules=True)
    # ------------------------------------------------------------------------------------------------------------------
    st.subheader('Analisis de precios individual')

    # Filtering by reference
    ref = st.selectbox("¿Que referencía desea analizar?", list(df_toilet["Producto"].unique()))
    product_ref = df_toilet[df_toilet["Producto"] == ref]

    c1, c2 = st.columns([2,1])
    # ------------------------------------------------------------------------------------------------------------------
    # Plotting line
    fig = px.line(data_frame=product_ref, x="Fecha", y="Precio", color="Producto", line_group="Producto",
                  title="Historico de precios de la referencía {}".format(ref),
                  width=1000, height=650,
                  # labels={"I_Valid": "Formatos"},
                  template="seaborn")

    fig.update_layout(modebar_add=["v1hovermode", "toggleSpikeLines"])
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

    fig.update_xaxes(dtick="d0.5", tickformat="%b %d\n%Y", rangeslider_visible=False)
    fig.update_xaxes(showline=True, linewidth=0.5, linecolor='black')
    fig.update_yaxes(showline=True, linewidth=0.5, linecolor='black')

    # Set x-axis and y-axis title
    fig['layout']['xaxis']['title'] = 'Fechas'
    fig['layout']['yaxis']['title'] = "Precios en COP"

    c1.plotly_chart(fig, use_container_width=True)
    # ------------------------------------------------------------------------------------------------------------------
    # Information from the product
    c2.subheader("Información del Producto")

    # Requesting the image
    urllib.request.urlretrieve(product_ref["Image_url"].iloc[-1], "image.png")
    image = Image.open('image.png')
    c2.image(image, caption='Producto seleccionado', width=300)

    # General information
    c2.markdown("**El producto es el:** {}".format(product_ref["Producto"].iloc[-1]))
    c2.markdown("**El SKU es el:** {}".format(product_ref["SKU"].iloc[-1]))
    c2.markdown("**El ultimo precio registrado es de:** ${:,} COP ".format(
        product_ref["Precio"].iloc[-1]).replace(',', '.'))
    c2.markdown("**La pagina web del producto es la:** {}".format(product_ref["URL"].iloc[-1]))

    # ------------------------------------------------------------------------------------------------------------------
    # Metrica
    # c2.metric(label="Ultimo Precio", value="{:,}".format(precios_mensual_ref["Precio"].values[-1]).replace(',', '.') +
    #                                       " COP", delta="{:,}".format(precios_mensual_ref["Precio"].values[-1] -
    #                                                                   precios_mensual_ref["Precio"].values[-2]
    #                                                                   ).replace(',', '.'),
    #          delta_color="off")
