# Python project Dashboard for pricing
# Creado por: Juan Monsalvo
# ----------------------------------------------------------------------------------------------------------------------
# Libraries import
# ----------------------------------------------------------------------------------------------------------------------
import os
import urllib.request

import pandas as pd

import streamlit as st
from PIL import Image
from st_aggrid import AgGrid

from Plot_Functions import plot_price_history

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

# Dropping duplicates in case the robot take two values by day
df.drop_duplicates(inplace=True)
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
if page == "Sanitarios":
    st.header('Historico de Precios Sanitarios')

    st.subheader('1) Analisis de precios global')
    # Filtering for Sanitario
    df_toilet_raw = df[df["Tipo"] != "Asiento"]

    # Filtering by marca
    marca_sel = st.selectbox("¿Que marca desea analizar?", df_toilet_raw["Marca"].unique(), 0)
    df_toilet = df_toilet_raw[df_toilet_raw["Marca"] == marca_sel]

    # Group by
    df_toilet_fam = df_toilet.pivot_table(index=["Fecha", "Familia"], values=["Precio"], fill_value=0,
                                          margins=False, aggfunc=max).reset_index()
    # ------------------------------------------------------------------------------------------------------------------
    # Plotting line plot
    fig = plot_price_history(df=df_toilet_fam, group="Familia", title="Historico de Precios de {}".format(marca_sel))
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Ver datos"):
        AgGrid(df_toilet, editable=False, sortable=True, filter=True, resizable=True, defaultWidth=5,
               fit_columns_on_grid_load=False, theme="streamlit",  # "light", "dark", "blue", "material"
               key="Toilet", reload_data=True,  # gridOptions=gridoptions,
               enable_enterprise_modules=True)
    # ------------------------------------------------------------------------------------------------------------------
    st.subheader('2) Analisis de precios individual')

    # Filtering by Family
    fam = st.selectbox("¿Que familia desea analizar?", list(df_toilet["Familia"].unique()))
    product_fam_ref = df_toilet[df_toilet["Familia"] == fam]

    c1, c2 = st.columns([2, 1])
    # ------------------------------------------------------------------------------------------------------------------
    # Plotting line
    fig = plot_price_history(df=product_fam_ref, group="Producto",
                             title="Historico de precios de la familia {}".format(fam), orient_h=True)
    c1.plotly_chart(fig, use_container_width=True)
    # ------------------------------------------------------------------------------------------------------------------
    # Information from the product
    c2.subheader("Información del Producto")

    # Filtering by reference
    ref = c2.selectbox("¿Que referencía desea ver?", list(product_fam_ref["Producto"].unique()))
    product_ref = product_fam_ref[product_fam_ref["Producto"] == ref]

    # Requesting the image
    urllib.request.urlretrieve(product_ref["Image_url"].iloc[-1], "image.png")
    image = Image.open('image.png')
    c2.image(image, caption='{} ({}) ${:,} COP'.format(product_ref["Producto"].iloc[-1],
                                                                  product_ref["SKU"].iloc[-1],
                                                                  product_ref["Precio"].iloc[-1]).replace(',', '.'),
             width=300)

    # General information
    c2.markdown("**La pagina web del producto es la:** {}".format(product_ref["URL"].iloc[-1]))

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    st.header("3) Comparación")

    comparación = {"Montecarlo Alongado Blanco": ["Nyren", "REACH ELONGADO BLANCO"],
                   "Prestigio": ["Nyren", "Solare Single"]
                   }

    var_key = st.selectbox("¿Que producto quieres comparar?", comparación.keys())

    elem_comp = comparación[var_key]
    var_key_list = [var_key]
    lista_comp = var_key_list + elem_comp

    df_filtro = df_toilet_raw[df_toilet_raw['Producto'].isin(lista_comp)]
    # ------------------------------------------------------------------------------------------------------------------
    # Plotting line
    fig = plot_price_history(df=df_filtro, group="Producto",
                             title="Historico de precios de {} vs la Competencía".format(var_key))
    st.plotly_chart(fig, use_container_width=True)

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    st.header("4) Selección de referencias a comparar")
    st.subheader("Información del Producto")
    df_toiletCorona = df_toilet_raw[df_toilet_raw["Marca"] == "Corona"]

    # Two columns
    cc1, cc2 = st.columns((1, 2))

    # Filtering by reference
    ref = cc1.selectbox("¿Que referencía desea ver?", list(df_toiletCorona["Producto"].unique()))
    product_ref = df_toiletCorona[df_toiletCorona["Producto"] == ref]

    # Requesting the image
    urllib.request.urlretrieve(product_ref["Image_url"].iloc[-1], "image.png")
    image = Image.open('image.png')
    cc1.image(image, caption='{} ({}) ${:,} COP'.format(product_ref["Producto"].iloc[-1],
                                                                  product_ref["SKU"].iloc[-1],
                                                                  product_ref["Precio"].iloc[-1]).replace(',', '.'),
             width=300)

    # General information
    cc1.markdown("**La pagina web del producto es la:** {}".format(product_ref["URL"].iloc[-1]))

    df_toiletComp = df_toilet_raw[df_toilet_raw["Marca"] != "Corona"]
    df_aux_comp = df_toiletComp.groupby("Producto").max().reset_index()

    filter_precio = df_aux_comp[(df_aux_comp["Precio"] <= product_ref["Precio"].iloc[-1] * 1.10) &
                                (df_aux_comp["Precio"] >= product_ref["Precio"].iloc[-1] * 0.9)]
    st.write(filter_precio)

    # -----------------------------------------------------------------------------------------------------------------
    cc2.subheader("Producto competencia")

    if st.checkbox("Organizar .csv file"):
        st.write(len(filter_precio))
        # Requesting the image
        for i in range(3):
            urllib.request.urlretrieve(filter_precio["Image_url"].iloc[i], "image.png")
            image = Image.open('image.png')
            cc2.image(image, caption=filter_precio["Producto"].iloc[i] + " " +
                                     "${:,} COP".format(filter_precio["Precio"].iloc[i]).replace(',', '.'), width=300)

            st.multiselect("¿Cuales quiere agregar?", filter_precio["Producto"].unique(), key="akkaka")


    # ----- PLOTLY---------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------------------------
    # Metrica
    # c2.metric(label="Ultimo Precio", value="{:,}".format(precios_mensual_ref["Precio"].values[-1]).replace(',', '.') +
    #                                       " COP", delta="{:,}".format(precios_mensual_ref["Precio"].values[-1] -
    #                                                                   precios_mensual_ref["Precio"].values[-2]
    #                                                                   ).replace(',', '.'),
    #          delta_color="off")
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
#  ASIENTOS
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
elif page == "Asientos":
    st.header('Historico de Precios Asientos Corona')

    st.markdown("---")
    st.subheader('1) Analisis de precios global')
    # Filtering for Asientos
    df_asiento = df[df["Tipo"] == "Asiento"]

    # Group by
    df_asiento_fam = df_asiento.pivot_table(index=["Fecha", "Familia"], values=["Precio"], fill_value=0,
                                          margins=False, aggfunc=max).reset_index()
    # ------------------------------------------------------------------------------------------------------------------
    # Plotting line plot
    fig = plot_price_history(df=df_asiento_fam, group="Familia", title="Historico de Precios Asientos Corona")
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Ver datos"):
        AgGrid(df_asiento, editable=False, sortable=True, filter=True, resizable=True, defaultWidth=5,
               fit_columns_on_grid_load=False, theme="streamlit",  # "light", "dark", "blue", "material"
               key="Toilet", reload_data=True,  # gridOptions=gridoptions,
               enable_enterprise_modules=True)
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    st.markdown("---")
    st.subheader('2) Analisis de precios individual')

    # Filtering by Family
    fam = st.selectbox("¿Que familia desea analizar?", list(df_asiento["Familia"].unique()))
    product_fam_ref = df_asiento[df_asiento["Familia"] == fam]

    c1, c2 = st.columns([2, 1])
    # ------------------------------------------------------------------------------------------------------------------
    # Plotting line
    fig = plot_price_history(df=product_fam_ref, group="Producto",
                             title="Historico de precios de la familia {}".format(fam), orient_h=True)
    c1.plotly_chart(fig, use_container_width=True)
    # ------------------------------------------------------------------------------------------------------------------
    # Information from the product

    # Filtering by reference
    ref = c2.selectbox("¿Que referencía desea ver?", list(product_fam_ref["Producto"].unique()))
    product_ref = product_fam_ref[product_fam_ref["Producto"] == ref]

    # Requesting the image
    urllib.request.urlretrieve(product_ref["Image_url"].iloc[-1], "image.png")
    image = Image.open('image.png')
    c2.image(image, caption='{} ({}) ${:,} COP'.format(product_ref["Producto"].iloc[-1],
                                                                  product_ref["SKU"].iloc[-1],
                                                                  product_ref["Precio"].iloc[-1]).replace(',', '.'),
             width=300)

    # General information
    c2.markdown("**La pagina web del producto es la:** {}".format(product_ref["URL"].iloc[-1]))
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    st.markdown("---")
    st.subheader('3) Analisis de Stock')

    # Filter by date
    fecha_filter = st.date_input("¿Que fecha desea revisar?")

    st.write("Estos son los productos que no tienen stock disponible en el momento.")

    # Filter last products without stock
    df_sin_stock = df_asiento[(df_asiento["Stock"] == "No") & (df_asiento["Fecha"] ==
                                                               str(fecha_filter))]

    AgGrid(df_sin_stock, editable=False, sortable=True, filter=True, resizable=True, defaultWidth=5,
           fit_columns_on_grid_load=False, theme="streamlit",  # "light", "dark", "blue", "material"
           key="Stock", reload_data=True,  # gridOptions=gridoptions,
           enable_enterprise_modules=True)



