# Python project Dashboard for pricing
# Creado por: Juan Monsalvo

# ----------------------------------------------------------------------------------------------------------------------
# Libraries import
# ----------------------------------------------------------------------------------------------------------------------
import plotly.express as px

# ----------------------------------------------------------------------------------------------------------------------
# Configuration and Global Variables
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# Function Definition
# ----------------------------------------------------------------------------------------------------------------------

def plot_price_history(df, group, title, orient_h=False):
    """
    Función que crea el gráfico de historico de precio.
    :param df: data frame con los precios y la historia.
    :param group: Texto para agrupar o dibujar por referencia o familia.
    :param title: Título de la gráfica.
    :param orient_h: Default FALSE, para poner los legend de manera horizontal.
    :return: fig: Objeto de plotly para graficar externamente.
    """
    # Plotting line plot
    fig = px.line(data_frame=df, x="Fecha", y="Precio", color=group, line_group=group,
                  title=title,
                  width=1000, height=600,
                  # labels={"I_Valid": "Formatos"},
                  template="seaborn")

    fig.update_traces(mode='lines+markers')
    fig.update_layout(modebar_add=["v1hovermode", "toggleSpikeLines"])

    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label="1m",
                         step="month",
                         stepmode="backward"),
                    dict(count=3,
                         label="3m",
                         step="month",
                         stepmode="backward"),
                    dict(count=1,
                         label="YTD",
                         step="year",
                         stepmode="todate"),
                ])
            ),
            type="date"
        ))

    if orient_h is True:
        fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

    fig.update_xaxes(dtick="d0.5", tickformat="%b %d\n%Y", rangeslider_visible=True)
    fig.update_xaxes(showline=True, linewidth=0.5, linecolor='black')

    fig.update_yaxes(tickprefix="$", tickformat=",.2f")
    fig.update_yaxes(showline=True, linewidth=0.5, linecolor='black')

    # Set x-axis and y-axis title
    fig['layout']['xaxis']['title'] = 'Fechas'
    fig['layout']['yaxis']['title'] = "Precios en COP"

    return fig
