import dash
import datetime as dt
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
import pandas as pd
from pandas import ExcelWriter
from pandas_datareader import data as pdr
import yfinance as yf
import os
from dash.exceptions import PreventUpdate

app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.COSMO])
print("Hello")
filepath = r"/Users/Sven/PycharmProjects/Minerviniscreener/ticker_components/Portfolio2.csv"


def get_file():
    #df = pd.read_csv(filepath)

    data = pd.read_csv(filepath)
    print(data)
    df = pd.DataFrame(data, columns=['Symbol', 'Stock'])
    print(df)

    # print(df)
    return html.Div(
        [
            html.Div(
                html.Table(
                    # Header
                    [html.Tr([html.Th("Stock - 52 Week Low - 52 Week High")])]
                    +
                    # Body
                    [
                        html.Tr(
                            [
                                html.Td(
                                    df["Stock"][ind]
                                )
                            ])

                        # for i in range(min(len(df), max_rows))
                        for ind in df.index

                    ]
                ),
                style={"height": "100%", "overflowY": "scroll"},
            ),
        ],
        style={"height": "100%"}, )


app.layout = html.Div(children=[
    html.H1("Hi"),
    html.P(get_file())
])

if __name__ == '__main__':
    app.run_server()
