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
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import psycopg2
from sqlalchemy import create_engine
import math

yf.pdr_override()
start = dt.datetime(2017, 12, 1)
now = dt.datetime.now()

#app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.COSMO])
#server = app.server

server = Flask(__name__)
app = dash.Dash(__name__, server=server, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.COSMO])
app.server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# This program runs the Mark Minvervini stockscreener.
# It reads the symbols from a xlsx file and writes the results of the stockscreener
# to a data table - with callback
# First try with database after watching charming data CRUD app and "pretty printed" youtube video

#app.server.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:your_password@localhost/test"
app.server.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:Dueffs1902@localhost/test"

db = SQLAlchemy(app.server)

engine = create_engine('postgresql://postgres:Dueffs1902@localhost/test')

class Product(db.Model):
    __tablename__ = 'portfolio'

    Symbol = db.Column(db.String(40), nullable=False, primary_key=True)
    Name = db.Column(db.String(40), nullable=False)

    def __init__(self, symbol, name):
        self.Symbol = symbol
        self.Name = name


filePath1 = r"ticker_components/SvenStocks9.xlsx"
filePath2 = r"ticker_components/ScreenOutput.xlsx"
filePath3 = r"ticker_components/Portfolio.xlsx"

#test method mit datum
#def check_date(a):
    #read db table
    #check if input a is part of db table "previousrun"
    #check if is still valid
            # no longer valid stocks
            # new stock


def get_stocks(filePath):
    #This method reads an xls file with all OMXS stocks and performs the minervini check on everyone of them.
    # filePath = r"/Users/Sven/pff/Python/DashApp6bootstrap/ticker_components/SvenStocks6.xlsx"
    stocklist = pd.read_excel(filePath)
    exportList = pd.DataFrame(columns=[
        'Stock', "50 Day MA", "150 Day Ma", "200 Day MA", "52 Week Low", "52 week High", "Date added", "last run"])
    #loop through all OMX stocks and perform the Minervini check
    for i in stocklist.index:
        stock = str(stocklist["Symbol"][i])

        try:
            df = pdr.get_data_yahoo(stock, start, now)

            smaUsed = [50, 150, 200]
            for x in smaUsed:
                sma = x
                df["SMA_" + str(sma)] = round(df.iloc[:,
                                              4].rolling(window=sma).mean(), 2)

            currentClose = df["Adj Close"][-1]
            #currentClose = pd.to_numeric(df["Adj Close"][-1])

            # print(currentClose)
            moving_average_50 = df["SMA_50"][-1]
            #moving_average_50 = pd.to_numeric(df["SMA_50"][-1])
            moving_average_150 = df["SMA_150"][-1]
            #moving_average_150 = pd.to_numeric(df["SMA_150"][-1])
            moving_average_200 = df["SMA_200"][-1]
            #moving_average_200 = pd.to_numeric(df["SMA_200"][-1])
            low_of_52week = min(df["Adj Close"][-260:])
            #low_of_52week = pd.to_numeric(low_of_52week)
            high_of_52week = max(df["Adj Close"][-260:])
            #high_of_52week = pd.to_numeric(high_of_52week)

            #date_added = "2020-11-11"
            #date_added = dt.datetime.today()
            date_added = dt.date.today()
            last_run = dt.date.today()


            try:
                moving_average_200_20 = df["SMA_200"][-20]
                #moving_average_200_20 = pd.to_numeric(moving_average_200_20)

            except Exception:
                moving_average_200_20 = 0

            # Condition 1: Current Price > 150 SMA and > 200 SMA
            if (currentClose > moving_average_150 > moving_average_200):
                cond_1 = True
                #print("Cond. 1 for " + stock + " is true")
            else:
                cond_1 = False
            # Condition 2: 150 SMA and > 200 SMA
            if (moving_average_150 > moving_average_200):
                cond_2 = True
                #print("Cond. 2 for " + stock + " is true")
            else:
                cond_2 = False
            # Condition 3: 200 SMA trending up for at least 1 month (ideally 4-5 months)
            if (moving_average_200 > moving_average_200_20):
                cond_3 = True
                #print("Cond. 3 for " + stock + " is true")
            else:
                cond_3 = False
            # Condition 4: 50 SMA> 150 SMA and 50 SMA> 200 SMA
            if (moving_average_50 > moving_average_150 > moving_average_200):
                # print("Condition 4 met")
                cond_4 = True
                #print("Cond. 4 for " + stock + " is true")
            else:
                # print("Condition 4 not met")
                cond_4 = False
            # Condition 5: Current Price > 50 SMA
            if (currentClose > moving_average_50):
                cond_5 = True
                #print("Cond. 5 for " + stock + " is true")
            else:
                cond_5 = False
            # Condition 6: Current Price is at least 30% above 52 week low (Many of the best are up 100-300% before coming out of consolidation)
            if (currentClose >= (1.3 * low_of_52week)):
                cond_6 = True
                #print("Cond. 6 for " + stock + " is true")
            else:
                cond_6 = False
            # Condition 7: Current Price is within 25% of 52 week high
            if (currentClose >= (.75 * high_of_52week)):
                cond_7 = True
                #print("Cond. 7 for " + stock + " is true")
            else:
                cond_7 = False
            #Add stock to exportList if all conditions are met.
            if (cond_1 and cond_2 and cond_3 and cond_4 and cond_5 and cond_6 and cond_7):
                exportList = exportList.append(
                    {'Stock': stock, "50 Day MA": moving_average_50, "150 Day Ma": moving_average_150,
                     "200 Day MA": moving_average_200, "52 Week Low": low_of_52week, "52 week High": high_of_52week, "Date added": date_added, "last run": last_run},
                    ignore_index=True)
                print("All conditions for " + stock + " are true.")

        except Exception:
            print("No data on " + stock)

    # print(exportList)
    #print(df.dtypes)

    return exportList


def get_stocks_portfolio_table(table):
    #this method gets the stocks from the 'portfolio' table in the db and checks all Minvervini conditions
    #stocklist = pd.read_excel(filePath)
    # read from database
    stocklist = pd.read_sql_table('portfolio', 'postgresql://postgres:Dueffs1902@localhost/test')

    exportList = pd.DataFrame(columns=[
        'Stock', "50 Day MA", "150 Day Ma", "200 Day MA", "52 Week Low", "52 week High", "Cond1", "Cond2", "Cond3",
        "Cond4", "Cond5", "Cond6", "Cond7", "Date added", "last run"])

    for i in stocklist.index:
        stock = str(stocklist["Symbol"][i])

        try:
            df = pdr.get_data_yahoo(stock, start, now)

            smaUsed = [50, 150, 200]
            for x in smaUsed:
                sma = x
                df["SMA_" + str(sma)] = round(df.iloc[:,
                                              4].rolling(window=sma).mean(), 2)

            currentClose = df["Adj Close"][-1]
            # print(currentClose)
            moving_average_50 = df["SMA_50"][-1]
            moving_average_150 = df["SMA_150"][-1]
            moving_average_200 = df["SMA_200"][-1]
            low_of_52week = min(df["Adj Close"][-260:])
            high_of_52week = max(df["Adj Close"][-260:])
            #date_added = "2020-11-20"
            #date_added = dt.datetime.today.strftime("%Y-%m-%d")
            #date_added = dt.datetime.today()
            date_added = dt.date.today()
            #date_added = dt.datetime.now.strftime("%d/%m/%Y %H:%M:%S")
            #date_added = df["Date added"]
            last_run = dt.date.today()


            try:
                moving_average_200_20 = df["SMA_200"][-20]

            except Exception:
                moving_average_200_20 = 0

            # Condition 1: Current Price > 150 SMA and > 200 SMA
            if (currentClose > moving_average_150 > moving_average_200):
                cond_1 = 1
                print("Cond. 1 for " + stock + " is true")
            else:
                cond_1 = 0
            # Condition 2: 150 SMA > 200 SMA
            if (moving_average_150 > moving_average_200):
                cond_2 = 1
                print("Cond. 2 for " + stock + " is true")
            else:
                cond_2 = 0
            # Condition 3: 200 SMA trending up for at least 1 month (ideally 4-5 months)
            if (moving_average_200 > moving_average_200_20):
                cond_3 = 1
                print("Cond. 3 for " + stock + " is true")
            else:
                cond_3 = 0
            # Condition 4: 50 SMA> 150 SMA and 50 SMA> 200 SMA
            if (moving_average_50 > moving_average_150 > moving_average_200):
                # print("Condition 4 met")
                cond_4 = 1
                print("Cond. 4 for " + stock + " is true")
            else:
                # print("Condition 4 not met")
                cond_4 = 0
            # Condition 5: Current Price > 50 SMA
            if (currentClose > moving_average_50):
                cond_5 = 1
                print("Cond. 5 for " + stock + " is true")
            else:
                cond_5 = 0
            # Condition 6: Current Price is at least 30% above 52 week low (Many of the best are up 100-300% before coming out of consolidation)
            if (currentClose >= (1.3 * low_of_52week)):
                cond_6 = 1
                print("Cond. 6 for " + stock + " is true")
            else:
                cond_6 = 0
            # Condition 7: Current Price is within 25% of 52 week high
            if (currentClose >= (.75 * high_of_52week)):
                cond_7 = 1
                print("Cond. 7 for " + stock + " is true")
            else:
                cond_7 = 0

            # if(cond_1 and cond_2 and cond_3 and cond_4 and cond_5 and cond_6 and cond_7):
            exportList = exportList.append(
                {'Stock': stock, "50 Day MA": moving_average_50, "150 Day Ma": moving_average_150,
                 "200 Day MA": moving_average_200, "52 Week Low": low_of_52week, "52 week High": high_of_52week,
                 "Cond1": cond_1, "Cond2": cond_2, "Cond3": cond_3, "Cond4": cond_4, "Cond5": cond_5, "Cond6": cond_6,
                 "Cond7": cond_7, "Date added": date_added, "last run" : last_run}, ignore_index=True)

        except Exception:
            print("No data on " + stock)

    # print(exportList)
    return exportList

def get_stocks_portfolio(filePath):
    # this method gets the stocks from the 'portfolio' xls file and checks all Minvervini conditions

    stocklist = pd.read_excel(filePath)
    # read from database
    exportList = pd.DataFrame(columns=[
        'Stock', "50 Day MA", "150 Day Ma", "200 Day MA", "52 Week Low", "52 week High", "Cond1", "Cond2", "Cond3",
        "Cond4", "Cond5", "Cond6", "Cond7", "Date added"])

    for i in stocklist.index:
        stock = str(stocklist["Symbol"][i])

        try:
            df = pdr.get_data_yahoo(stock, start, now)

            smaUsed = [50, 150, 200]
            for x in smaUsed:
                sma = x
                df["SMA_" + str(sma)] = round(df.iloc[:,
                                              4].rolling(window=sma).mean(), 2)

            currentClose = df["Adj Close"][-1]
            # print(currentClose)
            moving_average_50 = df["SMA_50"][-1]
            moving_average_150 = df["SMA_150"][-1]
            moving_average_200 = df["SMA_200"][-1]
            low_of_52week = min(df["Adj Close"][-260:])
            high_of_52week = max(df["Adj Close"][-260:])
            #date_added = df["Date added"]
            #date_added = "2020-11-11"
            #date_added = dt.datetime.today.strftime("%Y-%m-%d")
            #date_added = dt.datetime.now.strftime("%d/%m/%Y %H:%M:%S")
            #date_added = dt.datetime.today()
            date_added = dt.date.today()

            try:
                moving_average_200_20 = df["SMA_200"][-20]

            except Exception:
                moving_average_200_20 = 0

            # Condition 1: Current Price > 150 SMA and > 200 SMA
            if (currentClose > moving_average_150 > moving_average_200):
                cond_1 = 1
                print("Cond. 1 for " + stock + " is true")
            else:
                cond_1 = 0
            # Condition 2: 150 SMA > 200 SMA
            if (moving_average_150 > moving_average_200):
                cond_2 = 1
                print("Cond. 2 for " + stock + " is true")
            else:
                cond_2 = 0
            # Condition 3: 200 SMA trending up for at least 1 month (ideally 4-5 months)
            if (moving_average_200 > moving_average_200_20):
                cond_3 = 1
                print("Cond. 3 for " + stock + " is true")
            else:
                cond_3 = 0
            # Condition 4: 50 SMA> 150 SMA and 50 SMA> 200 SMA
            if (moving_average_50 > moving_average_150 > moving_average_200):
                # print("Condition 4 met")
                cond_4 = 1
                print("Cond. 4 for " + stock + " is true")
            else:
                # print("Condition 4 not met")
                cond_4 = 0
            # Condition 5: Current Price > 50 SMA
            if (currentClose > moving_average_50):
                cond_5 = 1
                print("Cond. 5 for " + stock + " is true")
            else:
                cond_5 = 0
            # Condition 6: Current Price is at least 30% above 52 week low (Many of the best are up 100-300% before coming out of consolidation)
            if (currentClose >= (1.3 * low_of_52week)):
                cond_6 = 1
                print("Cond. 6 for " + stock + " is true")
            else:
                cond_6 = 0
            # Condition 7: Current Price is within 25% of 52 week high
            if (currentClose >= (.75 * high_of_52week)):
                cond_7 = 1
                print("Cond. 7 for " + stock + " is true")
            else:
                cond_7 = 0

            # if(cond_1 and cond_2 and cond_3 and cond_4 and cond_5 and cond_6 and cond_7):
            exportList = exportList.append(
                {'Stock': stock, "50 Day MA": moving_average_50, "150 Day Ma": moving_average_150,
                 "200 Day MA": moving_average_200, "52 Week Low": low_of_52week, "52 week High": high_of_52week,
                 "Cond1": cond_1, "Cond2": cond_2, "Cond3": cond_3, "Cond4": cond_4, "Cond5": cond_5, "Cond6": cond_6,
                 "Cond7": cond_7, "Date added": date_added}, ignore_index=True)

        except Exception:
            print("No data on " + stock)

    # print(exportList)
    return exportList


def get_previous_run():
    #This methods reads the table 'previousrun' from the db and displays it as html table
    #df = pd.read_excel(filePath2)
    df = pd.read_sql_table('previousrun', 'postgresql://postgres:Dueffs1902@localhost/test')
    print("get_previous_run - read_sql_table")
    # print(df)
    return html.Div(
        [
            html.Div(
                html.Table(
                    # Header
                    [html.Tr([html.Th("Stock - 52 Week Low - 52 Week High - Date added - last run")])]
                    +
                    # Body
                    [
                        html.Tr(
                            [
                                html.Td(
                                    df["Stock"][ind]
                                ),
                                html.Td(
                                    df["52 Week Low"][ind]
                                ),
                                html.Td(
                                    df["52 week High"][ind]
                                ),
                                html.Td(
                                    df["Date added"][ind]
                                ),
                                html.Td(
                                    df["last run"][ind]
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


def get_legend():
    return html.Div(
        [
            html.Div(
                html.Table(
                    # Header
                    [html.Tr([html.Th("Condition - explanation")])]
                    +
                    # Body
                    [
                        html.Tr(
                            [
                                html.Td(
                                    "Condition 1:"
                                ),
                                html.Td(
                                    "Current Price > 150 SMA and > 200 SMA"
                                ),
                            ]),
                        html.Tr(
                            [
                                html.Td(
                                    "Condition 2:"
                                ),
                                html.Td(
                                    "150 SMA > 200 SMA"
                                ),
                            ]),
                        html.Tr(
                            [
                                html.Td(
                                    "Condition 3:"
                                ),
                                html.Td(
                                    "200 SMA trending up for at least 1 month (ideally 4-5 months)"
                                ),
                            ]),
                        html.Tr(
                            [
                                html.Td(
                                    "Condition 4:"
                                ),
                                html.Td(
                                    "50 SMA> 150 SMA and 50 SMA> 200 SMA"
                                ),
                            ]),
                        html.Tr(
                            [
                                html.Td(
                                    "Condition 5:"
                                ),
                                html.Td(
                                    "Current Price > 50 SMA"
                                ),
                            ]),
                        html.Tr(
                            [
                                html.Td(
                                    "Condition 6:"
                                ),
                                html.Td(
                                    "Current Price is at least 30% above 52 week low (Many of the best are up 100-300% before coming out of consolidation)"
                                ),
                            ]),
                        html.Tr(
                            [
                                html.Td(
                                    "Condition 7:"
                                ),
                                html.Td(
                                    "Current Price is within 25% of 52 week high"
                                ),
                            ]),
                    ]
                ),
                style={"height": "100%", "overflowY": "scroll"},
            ),
        ],
        style={"height": "100%"}, )


def get_portfolio():
    #this method reads the 'portfolio" table from db and displays all stocks as html table
    #df = pd.read_excel(filePath3)
    #df = pd.read_sql_table('portfolio', con=db.engine)
    df = pd.read_sql_table('portfolio', 'postgresql://postgres:Dueffs1902@localhost/test')
    print("get_portfolio - read_sql_table")
    #print(df)
    return html.Div(
        [
            html.Div(
                html.Table(
                    # Header
                    [html.Tr([html.Th("Stocks")])]
                    +
                    # Body
                    [
                        html.Tr(
                            [
                                html.Td(
                                    #xlsx version
                                    #df["Symbol"][ind]
                                    # database version
                                    df["Symbol"][ind]
                                ),
                                html.Td(
                                    #xlsx version
                                    #df["Stock"][ind]
                                    # database version
                                    df["name"][ind]
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


app.layout = html.Div(
    children=[
        dbc.Row(dbc.Col(html.H1("Marc Minvervini screener"),
                        width={'size': 9, 'offset': 3},
                        ),
                ),
        html.Br(),
        dbc.Row([dbc.Button(
            f"Open {graph}",
            id=f"button-{graph}",
            className="mb-3",
            color="primary",
        ) for graph in ["previous", "portfolio"]], justify="center"),
        html.Br(),
        # dbc.Row(dbc.Col(html.H2("Previous run"),
        #                width={'size': 5, 'offset': 1},)),
        # dbc.Row(dbc.Col(html.Div(id='datatable'))),

        dbc.Row([
            # dbc.Col(dbc.Collapse(get_previous_run(),id="collapse_datatable", is_open=False), width=5),
            dbc.Col(dbc.Collapse(dbc.Card(dbc.CardBody(get_previous_run()), color="primary", outline=True),
                                 id="collapse_datatable", is_open=False, className="w-80")),
            # dbc.Col(dbc.Collapse(html.H1("Hello datatable",id='datatable'),id="collapse_datatable", is_open=False), width=5),
            # dbc.Col(dbc.Collapse(html.Div(id='portfolio'),id="collapse_portfolio", is_open=False), width=5),
            dbc.Col(dbc.Collapse(dbc.Card(dbc.CardBody(get_portfolio()), color="primary", inverse=True),
                                 id="collapse_portfolio", is_open=False, className="w-80")),
            # dbc.Col(dbc.Collapse(get_portfolio(),id="collapse_portfolio", is_open=False), width=5)
        ]),

        # html.Br(),
        # dbc.Row(dbc.Col(html.H2("Portfolio"),
        #                width={'size': 5, 'offset': 1})),
        # dbc.Row(dbc.Col(html.Div(id='portfolio'))),
        html.Br(),
        dbc.Row(children=[dbc.Button("Run Minvervini screen", id="button_screen",
                                     color="primary", outline=True, className="mb-3", n_clicks=0),
                          dbc.Button("Check portfolio", id="button_portfolio",
                                     color="primary", className="mb-3", n_clicks=0)],
                justify='center'),

        html.Br(),
        dbc.Row([dbc.Button(
            f"Open {graph}",
            id=f"button-{graph}",
            className="mb-3",
            color="primary",
        ) for graph in ["legend"]], justify="center"),
        dbc.Row([
            # dbc.Col(dbc.Collapse(get_previous_run(),id="collapse_datatable", is_open=False), width=5),
            dbc.Col(
                dbc.Collapse(dbc.Card(dbc.CardBody(get_legend()), color="primary", outline=True), id="collapse_legend",
                             is_open=False, className="w-80")),
        ]),
        html.Br(),
        dbc.Row(
            dbc.Col(
                dbc.Spinner(children=[html.H1("Hier taucht gleich das Ergebnis auf.",
                                              id="container")], size="sm", color="warning")
            )),
        html.Br(),
        dbc.Row(
            dbc.Col(
                dbc.Spinner(children=[html.H1("Hier tauchen gleich die alten und neuen Ergebnisse auf.",
                                              id="container-changes")], size="sm", color="warning")
            )),
        html.Br(),
        dbc.Row(
            dbc.Col(
                dbc.Spinner(children=[html.H1("Hier taucht gleich das Ergebnis des Portfoliochecks auf.",
                                              id="datatable_portfolio")], color="warning"),
            )),
    ]
)


@app.callback(
    Output("collapse_datatable", "is_open"),
    [Input("button-previous", "n_clicks")],
    [State("collapse_datatable", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        # print(n)
        return not is_open
    # print("pling")
    return is_open


@app.callback(
    Output("collapse_portfolio", "is_open"),
    [Input("button-portfolio", "n_clicks")],
    [State("collapse_portfolio", "is_open")],
)
def toggle_collapse2(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("collapse_legend", "is_open"),
    [Input("button-legend", "n_clicks")],
    [State("collapse_legend", "is_open")],
)
def toggle_collapse3(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(Output('datatable', 'children'), [Input('button', 'n_clicks')])
def generate_html_table1(v):
    if v == None:
        raise PreventUpdate

    #df = pd.read_excel(filePath2)
    df = pd.read_sql_table('previousrun', 'postgresql://postgres:Dueffs1902@localhost/test')
    print("generate_html_table1 - read_sql_table")

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
                                ),
                                html.Td(
                                    df["52 Week Low"][ind]
                                ),
                                html.Td(
                                    df["52 week High"][ind]
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


@app.callback(Output('container', 'children'), [Input('button_screen', 'n_clicks')], prevent_initial_call=True)
#main method for minervini screen
def f(v):
    if v == None:
        raise PreventUpdate
    print(v)
    #df contains results of minervini screen = all stocks that passed the check
    df = get_stocks(filePath1)
    #pr_table contains table previousrun
    df2 = pd.read_sql_table('previousrun', 'postgresql://postgres:Dueffs1902@localhost/test')

    date_added = dt.date.today()
    #print("Neuer teil - 1")
    #print(df)
    #print("Neuer Teil - 2")
    #print(df2)

    #temp1 = pd.merge(df, df2, left_on='Stock', right_on='Stock')
    temp = pd.merge(df, df2, on='Stock', how='left', suffixes=('_left', '_right'))
    print("Temp 2:")
    print(temp)

    newFile = os.path.dirname(filePath2) + "/Temp.xlsx"
    print(filePath2)
    print(newFile)
    writer = ExcelWriter(newFile)
    temp.to_excel(writer, "Sheet1")
    writer.save()

    exportListNew = pd.DataFrame(columns=[
        'Stock', "Date added"])

    for i in temp.index:
        if temp["50 Day MA_left"][i] == temp["50 Day MA_right"][i]:
            print(temp["Stock"][i] + " ok")
        elif temp["50 Day MA_left"][i] != temp["50 Day MA_right"][i]:
            print(temp["Stock"][i] + " unequal")
            print(temp["50 Day MA_right"][i])
            print(temp["50 Day MA_left"][i])
            if math.isnan(temp["50 Day MA_right"][i]):
                exportListNew = exportListNew.append({'Stock': temp["Stock"][i], "Date added": date_added}, ignore_index=True)
            #if temp["50 Day MA_right"][i] == "nan":
                print(temp["Stock"][i] + " is right empty")
                #add todays date in "date added"
            elif math.isnan(temp["50 Day MA_left"][i]):
                print(temp["Stock"][i] + " is left empty")

    print(exportListNew)
    #compare df with existing db table previousrun (read it from db and save it as df2)
    #if stock from df exists in previousrun -> ok
    #if stock from df does not exist in previousrun -> new stock - date_added = today
    #if stock from previousrun is not part of new df -> stock no longer valid -> needs to be deleted from db

    if exportListNew.empty:
        print("Keine Änderungen seit gestern.")
        nochange ={'Stock':['Keine Änderung seit '],
                   'Date added':['1900-01-01']}
        nochangelist = pd.DataFrame(nochange)
        table2 = dbc.Table.from_dataframe(
            nochangelist, striped=True, bordered=True, responsive=True, hover=True)
    else:
        table2 = dbc.Table.from_dataframe(
        exportListNew, striped=True, bordered=True, responsive=True, hover=True)

    table1 = dbc.Table.from_dataframe(
        df, striped=True, bordered=True, responsive=True, hover=True)
    #print(df)

    #clear db table before saving the latest stocks
    try:
        db.session.query(Model).delete()
        db.session.commit()
    except:
        db.session.rollback()
    ##save to db
    pg = pd.DataFrame(df)
    pg.to_sql("previousrun", con=db.engine, if_exists='replace', index=False)
    ## end save to db

    newFile = os.path.dirname(filePath2) + "/ScreenOutput.xlsx"
    print(filePath2)
    print(newFile)
    writer = ExcelWriter(newFile)
    df.to_excel(writer, "Sheet1")
    writer.save()

    return dbc.Row(children=[
        dbc.Card(
            table2
        ),
        dbc.Card(
            table1
        )
    ])

# test for conditional formatting
@app.callback(Output('datatable_portfolio', 'children'), [Input('button_portfolio', 'n_clicks')],
              prevent_initial_call=True)
#callback for minervini check of portfolio
def generate_html_table5(v):
    if v == None:
        raise PreventUpdate

    #df = get_stocks_portfolio(filePath3)
    table = pd.read_sql_table('portfolio', 'postgresql://postgres:Dueffs1902@localhost/test')
    df = get_stocks_portfolio_table(table)
    print("generate_html_table5 - read_sql_table")
    print(df)
    print("generate_html_table5 - read_sql_table")

    table = dash_table.DataTable(
        id='table',
        # columns=[{"name": i, "id": i} for i in df.columns],
        # "50 Day MA", "150 Day Ma", "200 Day MA", "52 Week Low", "52 week High", "Cond1", "Cond2","Cond3","Cond4","Cond5","Cond6","Cond7"
        columns=[
            {'name': 'Stock', 'id': 'Stock', 'type': 'text'},
            {'name': '50 Day MA', 'id': '50 Day MA', 'type': 'numeric', 'hideable': True},
            {'name': '150 Day Ma', 'id': '150 Day Ma', 'type': 'numeric', 'hideable': True},
            {'name': '200 Day MA', 'id': '200 Day MA', 'type': 'numeric', 'hideable': True},
            {'name': '52 Week Low', 'id': '52 Week Low', 'type': 'numeric', 'hideable': True},
            {'name': '52 week High', 'id': '52 week High', 'type': 'numeric', 'hideable': True},
            {'name': 'Cond1', 'id': 'Cond1', 'type': 'numeric', 'hideable': True},
            {'name': 'Cond2', 'id': 'Cond2', 'type': 'numeric', 'hideable': True},
            {'name': 'Cond3', 'id': 'Cond3', 'type': 'numeric', 'hideable': True},
            {'name': 'Cond4', 'id': 'Cond4', 'type': 'numeric', 'hideable': True},
            {'name': 'Cond5', 'id': 'Cond5', 'type': 'numeric', 'hideable': True},
            {'name': 'Cond6', 'id': 'Cond6', 'type': 'numeric', 'hideable': True},
            {'name': 'Cond7', 'id': 'Cond7', 'type': 'numeric', 'hideable': True},
            {'name': 'Date added', 'id': 'Date added', 'type': 'text', 'hideable': True},
            {'name': 'last run', 'id': 'last run', 'type': 'text', 'hideable': True},
        ],
        data=df.to_dict('records'),
        style_data_conditional=[{
            'if': {
                'column_id': 'Stock',
                'filter_query': '{Cond1} > 0 && {Cond2} > 0 && {Cond3} > 0 && {Cond4} > 0 && {Cond5} > 0 && {Cond6} > 0 && {Cond7} > 0',

            },
            'backgroundColor': 'green',
            'color': 'white'
        },
            {'if': {
                'filter_query': '{Cond1} <  1',
                'column_id': 'Cond1'
            },
                'color': 'tomato',
                'fontWeight': 'bold'
            },
            {'if': {
                'filter_query': '{Cond1} >  0',
                'column_id': 'Cond1'
            },
                'backgroundColor': 'green',
                'color': 'white'
            },
            {'if': {
                'filter_query': '{Cond2} <  1',
                'column_id': 'Cond2'
            },
                'color': 'tomato',
                'fontWeight': 'bold'
            },
            {'if': {
                'filter_query': '{Cond2} >  0',
                'column_id': 'Cond2'
            },
                'backgroundColor': 'green',
                'color': 'white'
            },
            {'if': {
                'filter_query': '{Cond3} <  1',
                'column_id': 'Cond3'
            },
                'color': 'tomato',
                'fontWeight': 'bold'
            },
            {'if': {
                'filter_query': '{Cond3} >  0',
                'column_id': 'Cond3'
            },
                'backgroundColor': 'green',
                'color': 'white'
            },
            {'if': {
                'filter_query': '{Cond4} <  1',
                'column_id': 'Cond4'
            },
                'color': 'tomato',
                'fontWeight': 'bold'
            },
            {'if': {
                'filter_query': '{Cond4} >  0',
                'column_id': 'Cond4'
            },
                'backgroundColor': 'green',
                'color': 'white'
            },
            {'if': {
                'filter_query': '{Cond5} <  1',
                'column_id': 'Cond5'
            },
                'color': 'tomato',
                'fontWeight': 'bold'
            },
            {'if': {
                'filter_query': '{Cond5} >  0',
                'column_id': 'Cond5'
            },
                'backgroundColor': 'green',
                'color': 'white'
            },
            {'if': {
                'filter_query': '{Cond6} <  1',
                'column_id': 'Cond6'
            },
                'color': 'tomato',
                'fontWeight': 'bold'
            },
            {'if': {
                'filter_query': '{Cond6} >  0',
                'column_id': 'Cond6'
            },
                'backgroundColor': 'green',
                'color': 'white'
            },
            {'if': {
                'filter_query': '{Cond7} <  1',
                'column_id': 'Cond7'
            },
                'color': 'tomato',
                'fontWeight': 'bold'
            },
            {'if': {
                'filter_query': '{Cond7} >  0',
                'column_id': 'Cond7'
            },
                'backgroundColor': 'green',
                'color': 'white'
            }]
    )
    return dbc.Row(
        dbc.Card(
            table
        )
    )

#new try - method to show new and old stocks
#@app.callback(Output('container-changes', 'children'), [Input('button_screen', 'n_clicks')], prevent_initial_call=True)
#main method for minervini screen
#def f(v):
    #if v == None:
    #    raise PreventUpdate

    #df = get_stocks(filePath1)
    #table = dbc.Table.from_dataframe(
    #    df, striped=True, bordered=True, responsive=True, hover=True)
    #print(df)

    ##save to db
    #pg = pd.DataFrame(df)
    #pg.to_sql("previousrun", con=db.engine, if_exists='replace', index=False)
    ## end save to db

    #newFile = os.path.dirname(filePath2) + "/ScreenOutput.xlsx"
    #print(filePath2)
    #print(newFile)
    #writer = ExcelWriter(newFile)
    #df.to_excel(writer, "Sheet1")
    #writer.save()
    #return ''
    #return dbc.Row(
    #    dbc.Card(
    #        table
    #    )
    #)


if __name__ == '__main__':
    app.run_server(debug=True)
