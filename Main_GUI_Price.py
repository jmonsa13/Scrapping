# Python project Dashboard for pricing
# Creado por: Juan Monsalvo

# ----------------------------------------------------------------------------------------------------------------------
# Libraries import
# ----------------------------------------------------------------------------------------------------------------------
import pandas as pd
import os
import streamlit as st

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

tabs = ["Decorceramica", "Homecenter", "Corona"]
page = st.sidebar.radio("Paginas", tabs, index=0)
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Initial page
st.title('💲 Monitoreo de Precios - Corona 🤖')

# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
if page == "Decorceramica":
    st.header('Historico de Precios Decorceramica en Sanitarios Two Pieces')

    st.subheader('Analisis de precios global')

    # Folder path definition
    directory = './Data'
    files = os.listdir(directory)

    # Empty data frame
    precios_mensual = pd.DataFrame()

    # Loading the DF of each month in a unique DF
    for file in files:
        precios_mensual = pd.concat([precios_mensual, load_data(folder=directory + '/', filename=file)])

    # ------------------------------------------------------------------------------------------------------------------
    # Plotting line plot
    fig = px.line(data_frame=precios_mensual, x="Date", y="Price", color="Product", line_group="Product",
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
    # ------------------------------------------------------------------------------------------------------------------
    # Plotting bar
    fig = px.bar(data_frame=precios_mensual, x="Date", y="Price", color="Product",
                 title="Historico Precios Decorceramica Two Pieces",
                 width=1000, height=600,
                 # labels={"I_Valid": "Formatos"},
                 template="seaborn")


    fig.update_layout(barmode='group', bargap=0.3, bargroupgap=0.02, xaxis_tickangle=0)
    fig.update_layout(modebar_add=["v1hovermode", "toggleSpikeLines"])

    fig.update_xaxes(dtick="d0.5", tickformat="%b %d\n%Y", rangeslider_visible=False)
    fig.update_xaxes(showline=True, linewidth=0.5, linecolor='black')
    fig.update_yaxes(showline=True, linewidth=0.5, linecolor='black')

    # Set x-axis and y-axis title
    fig['layout']['xaxis']['title'] = 'Fechas'
    fig['layout']['yaxis']['title'] = "Precios en COP"

    st.plotly_chart(fig, use_container_width=True)
    # ------------------------------------------------------------------------------------------------------------------
    st.subheader('Analisis de precios individual')

    # Filtering by reference
    ref = st.selectbox("¿Que referencía desea analizar?", list(precios_mensual["Product"].unique()))
    precios_mensual_ref = precios_mensual[precios_mensual["Product"] == ref]

    c1, c2 = st.columns(2)
    # ------------------------------------------------------------------------------------------------------------------
    # Plotting bar
    fig = make_subplots(specs=[[{"secondary_y": False}]])

    fig.add_trace(go.Bar(
        x=precios_mensual_ref["Date"],
        y=precios_mensual_ref["Price"],
        text=precios_mensual_ref["Price"], textposition='auto',
        name=ref))

    title = "Historico de precios de la referencía {}".format(ref)
    fig.update_layout(width=1000, height=600, legend=dict(orientation="v"), template="seaborn", title=title)
    fig.update_layout(barmode='group', bargap=0.3, bargroupgap=0.02, xaxis_tickangle=0)
    fig.update_layout(modebar_add=["v1hovermode", "toggleSpikeLines"])

    fig.update_xaxes(dtick="d0.5", tickformat="%b %d\n%Y", rangeslider_visible=False)
    fig.update_xaxes(showline=True, linewidth=0.5, linecolor='black')
    fig.update_yaxes(showline=True, linewidth=0.5, linecolor='black')

    # Set x-axis and y-axis title
    fig['layout']['xaxis']['title'] = 'Fechas'
    fig['layout']['yaxis']['title'] = "Precios en COP"

    c1.plotly_chart(fig, use_container_width=True)
    # ------------------------------------------------------------------------------------------------------------------
    # Metrica
    c2.metric(label="Ultimo Precio", value="{:,}".format(precios_mensual_ref["Price"].values[-1]).replace(',', '.') +
                                           " COP", delta="{:,}".format(precios_mensual_ref["Price"].values[-1] -
                                                                       precios_mensual_ref["Price"].values[-2]
                                                                       ).replace(',', '.'),
              delta_color="off")
