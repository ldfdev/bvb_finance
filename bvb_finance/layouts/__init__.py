from dash import html, dash_table, dcc, callback, Output, Input
import datetime
import enum
import logging
import pandas as pd
from bvb_finance.company_reports import portfolio_loader
from bvb_finance.company_reports.BVB_Report import BVB_Report
from bvb_finance.company_reports import dto
from bvb_finance import containers
from bvb_finance import datetime_conventions
import bvb_finance

logger = bvb_finance.getLogger()

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
    Output(component_id='save-db-button-notification-ui', component_property='children'),
    Input(component_id='save-db-button', component_property='n_clicks'),
    prevent_initial_call=True
)
def update_output(n_clicks):
    file_path = containers.export_mongo_container_db()
    return 'Database content has been exported to {}'.format(
        file_path
    )

# range picker to explore company information
class RadioButtonRange(enum.Enum):
    today = 'Today'
    this_week = 'This Week'
    this_month = 'This Month'

def get_radio_button_to_search_for_company_reports():
    return html.Div([
        html.Div(id='range-picker-radiobar-ui',
                 children='Choose an option to search for company reports'),
        html.Div(id='failures-radiobar-ui',
                 children=''),
        dcc.RadioItems(options=[e.value for e in RadioButtonRange], value=RadioButtonRange.today.value, id='range-picker-radiobar'),
    ])

@callback(
    Output(component_id='company-reports-table', component_property='data'),
    Output(component_id='range-picker-radiobar-ui', component_property='children'),
    Output(component_id='failures-radiobar-ui', component_property='children'),
    Input(component_id='range-picker-radiobar', component_property='value')
)
def pick_range(user_option):
    start_date_time = None
    now = datetime.datetime.now()
    end_date_time = datetime.datetime(now.year, now.month, now.day, hour=23, minute=59, second=59)
    if user_option == RadioButtonRange.today.value:
        start_date_time = datetime.datetime(now.year, now.month, now.day, hour=0, minute=0, second=0)
    elif user_option == RadioButtonRange.this_week.value:
        start_date_time = datetime.datetime(now.year, now.month, now.weekday(), hour=0, minute=0, second=0)
    elif user_option == RadioButtonRange.this_month.value:
        start_date_time = datetime.datetime(now.year, now.month, day=1, hour=0, minute=0, second=0)
    
    company_data, failures = search_reports_on_bvb_and_save(start_date_time, end_date_time)
    return [
        company_data,
        'You have chosen start date {} & end date {}'.format(
            start_date_time.strftime(datetime_conventions.date_time_format),
            end_date_time.strftime(datetime_conventions.date_time_format)),
        '{} Failures for these tickers were reported: {}'.format(
            len(failures),
            failures
        )
    ]
 

def search_reports_on_bvb_and_save(start_date, end_date):
    logger.info(f'Searching for reports between start_date {start_date} and end_date {end_date}')
    tickers = portfolio_loader.load_portfolio_tickers()
    data = list()
    failures = []
    for ticker in tickers:
        try:
            logger.info(f'Collecting Website_Company data for ticker {ticker}')
            report: dto.Website_Company = BVB_Report.search_reports_on_bvb_and_save(ticker)
            for doc in report.documents:
                if doc.modification_date < start_date.date():
                    logger.info(f"Skipping document {report.ticker}:{doc.file_name} as it is older than {start_date.date()}")
                    continue
                
                line = [report.ticker, doc.file_name, doc.modification_date.strftime(datetime_conventions.date_dormat)]
                data.append(line)
        except Exception as exc:
            logger.warning(f'Failed to gather Website_Company data for {ticker}', exc)
            failures.append(ticker)

    report_df = pd.DataFrame(data, columns=['Ticker', 'Report', 'Raport Date'])
    logger.info(f'Search reports on bvb completed for the following tickers: {tickers}.' +
                f'\n gathered data:\n{report_df}')
    
    if len(failures) > 0:
        logger.warning(f"These tickers were failed to process: {failures}")
    return report_df.to_dict('records'), failures