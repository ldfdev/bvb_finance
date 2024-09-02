import dash
import pandas as pd
import datetime
import dash_bootstrap_components as dbc
from . import common
from bvb_finance.portfolio import dto
from bvb_finance import portfolio
from bvb_finance import datetime_conventions
from bvb_finance.common import numeric 
from bvb_finance.rest_api import portfolio as rest_api_portfolio

portfolio_amount_invested = "Portfolio Amout Invested: {}"
portfolio_roi = "Portfolio Return on Investment: {}"

def get_table():
    table = common.get_table()
    table.id = 'portfolio-all-companies-table-id'
    return table

def get_card_from_acquisition(acquisition: dto.Acquisition) -> dbc.Card:
    table = get_table()
    table.id = str()
    table.css = [
        {
            'selector': 'tr:first-child',
            'rule': 'display: none',
        },
    ]
    table.export_format=None

    # adjust Acquisition dictionary to match UI format
    _dict = {k:v for k, v in acquisition.dict.items()}
    _dict["date"] = _dict["date"].strftime(datetime_conventions.date_format)
    
    table.data = [{"Key": k, "Value": v} for k, v in _dict.items()]
    return dbc.Card(
        dbc.CardBody(
            [
                dash.html.H3(acquisition.symbol, className="card-title"),
                table,
            ]
        ),
        style={
            "border": "1px solid black",
            "border-radius": "10px",
            "box-shadow": "5px 5px 5px hsl(182, 96%, 29%)",
            "padding": "10px",
            "margin": "10px",
            "text-align": "center",
            "max-width": "fit-content",
            "display": "inline-block"
        },
    )

def get_layout():
    acquisitions: list[dto.Acquisition] = rest_api_portfolio.get_acquisitions_data()

    return dash.html.Div([
        dash.html.H4(children="My Acquisitions"),
        dash.html.Div([
                get_card_from_acquisition(a) for a in acquisitions
            ],
            style = {
                "width": "90%",
                "height": "auto",
                "overflow-x": "scroll",
                "scroll-behavior": "smooth",
                "display": "flex",
                "flex-direction": "row",
                "align-items": "left",
                # "justify-content": "center"
            }
        ),
        dash.html.Div(id='portfolio-status-div',
                 children="Press 'Confirm choice' to load portfolio data"),
        dash.html.Div([
            dash.html.Button('Confirm choice', id='portfolio-confirm-choice-button', n_clicks=0),
        ]),
        dash.html.Div([
            dash.html.H3(id='portfolio-amount-invested-component',
                         children = portfolio_amount_invested.format(" - ")),
            dash.html.H3(id='portfolio-roi-component',
                         children = portfolio_roi.format(" - "))
        ]),
        dash.html.Div(id='portfolio-statistics-graph-div',
                children=""
        ),
        dash.html.Div([
            get_table()
        ]),
    ])

@dash.callback(
    dash.Output(component_id='portfolio-all-companies-table-id', component_property='data', allow_duplicate=True),
    dash.Output(component_id='portfolio-status-div', component_property='children', allow_duplicate=True),
    dash.Output(component_id='portfolio-amount-invested-component', component_property='children', allow_duplicate=True),
    dash.Output(component_id='portfolio-roi-component', component_property='children', allow_duplicate=True),
    dash.Output(component_id='portfolio-statistics-graph-div', component_property='children', allow_duplicate=True),
    dash.Input(component_id='portfolio-confirm-choice-button', component_property='n_clicks'),
    prevent_initial_call=True,
    running=common.disable_component_till_completion('portfolio-confirm-choice-button')
)
def load_market_cap_data_callback(n_clicks):
    ui_payload: list[dto.UIDataDict] = portfolio.obtain_portfolio_data()
    sum_invested = numeric.safe_sum(u["invested_sum"] for u in ui_payload)
    market_value = numeric.safe_sum(u["market_value"] for u in ui_payload)
    data_actualizare = list(set(datetime_conventions.to_bvb_finance_date_format(u["market_value_date"]) for u in ui_payload))
    
    figure = portfolio.build_portfoloio_figures(ui_payload)

    return [
        ui_payload,
        f"Ultima actualizare: {data_actualizare}",
        portfolio_amount_invested.format(sum_invested),
        portfolio_roi.format(portfolio.compute_roi(sum_invested, market_value)),
        dash.dcc.Graph(figure=figure)
    ]