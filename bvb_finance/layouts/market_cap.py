import dash
import pandas as pd
from . import common
from bvb_finance.marketcap import bvb_rader

def get_table():
    table = common.get_table()
    table.id = 'market-cap-table-id'
    return table

def get_layout():
    return dash.html.Div([
        dash.html.Div(id='radio-bar-user-option-div',
                 children='Choose an option to search for company reports'),
        dash.html.Div([
            dash.html.Button('Confirm choice', id='market-cap-confirm-choice-button', n_clicks=0),
        ]),
        dash.html.Div([
            get_table()
        ]),
    ])

@dash.callback(
    dash.Output(component_id='market-cap-table-id', component_property='data', allow_duplicate=True),
    dash.Input(component_id='market-cap-confirm-choice-button', component_property='n_clicks'),
    prevent_initial_call=True,
    running=common.disable_component_till_completion('market-cap-confirm-choice-button')
)
def load_market_cap_data_callback(n_clicks):
    return bvb_rader.get_market_cap_data()
