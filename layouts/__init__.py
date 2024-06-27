from dash import html, dash_table, dcc, callback, Output, Input

from bvb_finance.company_reports import portfolio_loader
from bvb_finance import containers

# Company tickers layout
def get_company_tickers_layout():
    return html.Ul([html.Li(x) for x in portfolio_loader.load_portfolio_tickers()])

# button to save mongo db State
def get_button_to_save_db_content():
    return html.Div([
        html.Button('Export Database content', id='save-db-button', n_clicks=0),
        html.Div(id='save-db-button-notification-ui',
                children='Click to export database content')
    ])

@callback(
    Output('save-db-button-notification-ui', 'children'),
    Input('save-db-button', 'n_clicks'),
    prevent_initial_call=True
)
def update_output(n_clicks):
    file_path = containers.export_mongo_container_db()
    return 'Database content has been exported to {}'.formay(
        file_path
    )
