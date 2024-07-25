import dash
import pandas as pd
import datetime
from . import common
from bvb_finance.portfolio import dto
from bvb_finance import portfolio
from bvb_finance import datetime_conventions
from bvb_finance.common import numeric 

portfolio_amount_invested = "Portfolio Amout Invested: {}"
portfolio_roi = "Portfolio Return on Investment: {}"

def get_table():
    table = common.get_table()
    table.id = 'portfolio-all-companies-table-id'
    return table

def get_layout():
    return dash.html.Div([
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
        dash.html.Div([
            get_table()
        ]),
    ])

@dash.callback(
    dash.Output(component_id='portfolio-all-companies-table-id', component_property='data', allow_duplicate=True),
    dash.Output(component_id='portfolio-status-div', component_property='children', allow_duplicate=True),
    dash.Output(component_id='portfolio-amount-invested-component', component_property='children', allow_duplicate=True),
    dash.Output(component_id='portfolio-roi-component', component_property='children', allow_duplicate=True),
    dash.Input(component_id='portfolio-confirm-choice-button', component_property='n_clicks'),
    prevent_initial_call=True,
    running=common.disable_component_till_completion('portfolio-confirm-choice-button')
)
def load_market_cap_data_callback(n_clicks):
    ui_payload: dto.UIDataDict = portfolio.obtain_portfolio_data()
    sum_invested = numeric.safe_sum(u["invested_sum"] for u in ui_payload)
    market_value = numeric.safe_sum(u["market_value"] for u in ui_payload)
    data_actualizare = list(set(datetime_conventions.to_bvb_finance_date_format(u["market_value_date"]) for u in ui_payload))
    return [
        ui_payload,
        f"Ultima actualizare: {data_actualizare}",
        portfolio_amount_invested.format(sum_invested),
        portfolio_roi.format(portfolio.compute_roi(sum_invested, market_value))
    ]