import dash
import pandas as pd
from . import common
from bvb_finance.marketcap import bvb_radar
from bvb_finance.marketcap import dto

def get_table():
    table = common.get_table()
    table.id = 'market-cap-table-id'
    return table

def get_layout():
    return dash.html.Div([
        dash.html.Div(id='market-cap-status-div',
                 children="Press 'Confirm choice' to search for market cap reports"),
        dash.html.Div([
            dash.html.Button('Confirm choice', id='market-cap-confirm-choice-button', n_clicks=0),
        ]),
        dash.html.Div([
            get_table()
        ]),
    ])

@dash.callback(
    dash.Output(component_id='market-cap-table-id', component_property='data', allow_duplicate=True),
    dash.Output(component_id='market-cap-status-div', component_property='children', allow_duplicate=True),
    dash.Input(component_id='market-cap-confirm-choice-button', component_property='n_clicks'),
    prevent_initial_call=True,
    running=common.disable_component_till_completion('market-cap-confirm-choice-button')
)
def load_market_cap_data_callback(n_clicks):
    ui_payload: dto.MarketCapDataUiPayload = bvb_radar.get_market_cap_data()

    return [
        ui_payload.data,
        f"Data Citire: {ui_payload.modofication_date}"
    ]
