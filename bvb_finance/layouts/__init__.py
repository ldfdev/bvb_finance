import dash
import datetime
import dataclasses
import enum
import pandas as pd
import typing
from bvb_finance.company_reports import portfolio_loader
from bvb_finance.company_reports.BVB_Report import BVB_Report
from bvb_finance.company_reports import dto
from bvb_finance import containers
from bvb_finance import datetime_conventions
import bvb_finance

__all__ = [
    'get_company_tickers_layout',
    'get_button_to_save_db_content',
    'get_radio_bar_to_search_for_company_reports',
    'get_component_to_load_db_snapshot',
    'get_table',
]

logger = bvb_finance.getLogger()

# types
Failures: typing.TypeAlias = list[str]
DataframeFailuresTuple: typing.TypeAlias = typing.Tuple[pd.DataFrame, Failures]
WebsitecompanyFailuresTuple: typing.TypeAlias = typing.Tuple[typing.Iterable[dto.Website_Company], Failures]

# Company tickers layout
def get_company_tickers_layout():
    return dash.html.Ul([dash.html.Li(x) for x in portfolio_loader.load_portfolio_tickers()])

# button to save mongo db State
def get_button_to_save_db_content():
    return dash.html.Div([
        dash.html.Button('Export Database content', id='save-db-button', n_clicks=0),
        dash.html.Div(id='save-db-button-notification-ui',
                children='Click to export database content')
    ])

@dash.callback(
    dash.Output(component_id='save-db-button-notification-ui', component_property='children'),
    dash.Input(component_id='save-db-button', component_property='n_clicks'),
    prevent_initial_call=True
)
def get_button_to_save_db_content_callback(n_clicks):
    file_path = containers.export_mongo_container_db()
    return 'Database content has been exported to {}'.format(
        file_path
    )

# range picker to explore company information
class RadioButtonRange(enum.Enum):
    today = 'Today'
    this_week = 'This Week'
    this_month = 'This Month'

def get_radio_bar_to_search_for_company_reports():
    return dash.html.Div([
        dash.html.Div(id='radio-bar-user-option-div',
                 children='Choose an option to search for company reports'),
        dash.html.Div(id='radio-bar-failures-div'),
        dash.dcc.RadioItems(options=[e.value for e in RadioButtonRange], value=RadioButtonRange.today.value, id='range-picker-radiobar'),
        dash.html.Div([
            dash.html.Button('Confirm choice', id='radio-bar-confirm-choice-button', n_clicks=0),
            dash.html.Button('Retry failed companies', id='radio-bar-retry-failed-button', n_clicks=0, disabled=True),
        ]),
    ])

def load_db_snapshots_from_local_storage() -> list[str]:
    return containers.load_exported_data()

def get_component_to_load_db_snapshot():
    return dash.html.Div([
        dash.html.Div(id='db_snapshot-div',
                 children='Load database snapshot'),
        dash.html.Div(id='db_snapshot-failures-div'),
        dash.dcc.RadioItems(options=[file for file in load_db_snapshots_from_local_storage()], id='db_snapshot-radiobar'),
        dash.html.Div([
            dash.html.Button('Confirm choice', id='db_snapshot-confirm-choice-button', n_clicks=0)
        ]),
    ])

def get_table():
    return dash.dash_table.DataTable(
        id='company-reports-table',
        data=[],
        page_size=40,
        style_header={
            'backgroundColor': 'rgb(30, 30, 30)',
            'color': 'white',
            'fontWeight': 'bold'
        },
        style_data={
            'backgroundColor': 'rgb(50, 50, 50)',
            'color': 'white'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(94, 194, 219)',
                'color': 'black'
            }
        ],
    )

@dash.callback(
    dash.Output(component_id='db_snapshot-failures-div', component_property='children'),
    dash.Output(component_id='company-reports-table', component_property='data', allow_duplicate=True),
    dash.Input(component_id='db_snapshot-radiobar', component_property='value'),
    dash.Input(component_id='db_snapshot-confirm-choice-button', component_property='n_clicks'),
    prevent_initial_call=True,
    running=[dash.Output(component_id='db_snapshot-confirm-choice-button', component_property='disabled'), True, False]
)
def get_component_to_load_db_snapshot_callback(db_snapshot_file, n_clicks):
    if 'db_snapshot-confirm-choice-button' != dash.ctx.triggered_id:
        return dash.no_update
    
    containers.import_db_snapshot_to_mongo(db_snapshot_file)
    reports: list[dto.Website_Company] = BVB_Report.load_reports_from_mongo()
    reports_df: pd.DataFrame = convert_website_company_collection_to_dataframe(reports)
    return [
        f'Database snapshot {db_snapshot_file} has been used',
        reports_df,
    ]


@dash.callback(
    dash.Output(component_id='radio-bar-failures-div', component_property='children', allow_duplicate=True),
    dash.Output(component_id='radio-bar-retry-failed-button', component_property='disabled', allow_duplicate=True),
    dash.Input(component_id='radio-bar-retry-failed-button', component_property='n_clicks'),
    prevent_initial_call=True
)
def get_radio_bar_to_search_for_company_reports_run_retry_logic_callback(n_clicks):
    failures = []
    return (_display_failures_message(failures), True)

@dash.callback(
    dash.Output(component_id='company-reports-table', component_property='data', allow_duplicate=True),
    dash.Output(component_id='radio-bar-user-option-div', component_property='children'),
    dash.Output(component_id='radio-bar-failures-div', component_property='children', allow_duplicate=True),
    dash.Output(component_id='radio-bar-retry-failed-button', component_property='disabled', allow_duplicate=True),
    dash.Input(component_id='range-picker-radiobar', component_property='value'),
    dash.Input(component_id='radio-bar-confirm-choice-button', component_property='n_clicks'),
    prevent_initial_call=True,
    running=[dash.Output(component_id='radio-bar-confirm-choice-button', component_property='disabled'), True, False]
)
def get_radio_bar_to_search_for_company_reports_callback(user_option: RadioButtonRange, n_clicks: int):
    def _display_formatted_date(start_date_time, end_date_time):
        return 'You have chosen start date {} & end date {}'.format(
            start_date_time.strftime(datetime_conventions.date_time_format),
            end_date_time.strftime(datetime_conventions.date_time_format)
        )
    
    if 'radio-bar-confirm-choice-button' != dash.ctx.triggered_id:
        return dash.no_update
    
    start_date_time = None
    now = datetime.datetime.now()
    end_date_time = datetime.datetime(now.year, now.month, now.day, hour=23, minute=59, second=59)
    if user_option == RadioButtonRange.today.value:
        start_date_time = datetime.datetime(now.year, now.month, now.day, hour=0, minute=0, second=0)
    elif user_option == RadioButtonRange.this_week.value:
        first_week_day = datetime.datetime(now.year, now.month, now.weekday(), hour=0, minute=0, second=0)
        while (first_week_day + datetime.timedelta(days=7)).day <= now.day:
            first_week_day += datetime.timedelta(days=7)
        start_date_time = first_week_day
    elif user_option == RadioButtonRange.this_month.value:
        start_date_time = datetime.datetime(now.year, now.month, day=1, hour=0, minute=0, second=0)
    
    # company_data, failures = search_reports_on_bvb_and_save(start_date_time, end_date_time)
    company_data = convert_website_company_collection_to_dataframe([
        dto.Website_Company(name='Demo', ticker='DEMO', documents = [])
    ])
    failures = ['ABC']

    return [
        company_data,
        _display_formatted_date(start_date_time, end_date_time),
        _display_failures_message(failures),
        False
    ]

def _display_failures_message(failures: list[str]):
    if len(failures) == 0:
        return 'There are no failures'
    return f'{len(failures)} Failures for these tickers were reported: {failures}'

def get_reports_from_tickers(tickers: list[str]) -> WebsitecompanyFailuresTuple:
    logger.info(f'Searching for reports for the folloiwng tickers {tickers}')
    reports = list()
    failures = list()
    for ticker in tickers:
        logger.info(f'Collecting Website_Company data for ticker {ticker}')
        try:
            report: dto.Website_Company = BVB_Report.search_report_on_bvb_and_save(ticker)
            reports.append(report)
        except Exception as exc:
            logger.warning(f'Failed to gather Website_Company data for {ticker}', exc)
            failures.append(ticker)
    return (reports, failures,)

def filter_reports_based_on_date(reports: typing.Iterable[dto.Website_Company], start_date, end_date) -> typing.Iterable[dto.Website_Company]:
    filtered_reports = list()
    for report in reports:
        filtered_report: dto.Website_Company = dataclasses.replace(report)
        filtered_report.documents.clear()
        for doc in report.documents:
            if doc.modification_date < start_date.date():
                logger.info(f"Skipping document {report.ticker}:{doc.file_name} as it is older than {start_date.date()}")
                continue
            filtered_report.documents.append(doc)
    return filtered_reports

def search_reports_on_bvb_and_save(start_date, end_date) -> DataframeFailuresTuple:
    logger.info(f'Searching for reports between start_date {start_date} and end_date {end_date}')
    tickers = portfolio_loader.load_portfolio_tickers()
    reports, failures = get_reports_from_tickers(tickers)
    filtered_reports = filter_reports_based_on_date(reports, start_date, end_date)

    if len(failures) > 0:
        logger.warning(f"These tickers were failed to process: {failures}")
    return (
        convert_website_company_collection_to_dataframe(filtered_reports),
        failures,
    )

def convert_website_company_collection_to_dataframe(website_company_iter: typing.Iterable[dto.Website_Company]) -> pd.DataFrame:
    logger.info('Search reports on bvb completed for the following tickers: {}.'.format(
        [w_c.ticker for w_c in website_company_iter]
    ))
    data = list()
    for report in website_company_iter:
        for doc in report.documents:
            data.append([
                report.ticker,
                doc.file_name,
                doc.modification_date.strftime(datetime_conventions.date_dormat)
            ])
    report_df = pd.DataFrame(data, columns=['Ticker', 'Report', 'Data Raport'])
    logger.info(f'gathered data:\n{report_df}')
    
    return report_df.to_dict('records')
