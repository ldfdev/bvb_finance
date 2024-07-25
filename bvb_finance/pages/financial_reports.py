import dash
import bvb_finance
import datetime
from bvb_finance import layouts
from bvb_finance import logging

logger = logging.getLogger()
dash.register_page(__name__, name='Financial Reports available on BVB for my portfolio', path='/financial_reports')


# App layout
layout = [
    dash.html.Div(children='Financial Reports Data BVB'),
    dash.html.Hr(),
    layouts.get_company_tickers_layout(),
    layouts.get_radio_bar_to_search_for_company_reports(),
    layouts.get_component_to_load_db_snapshot(),
    dash.html.Div([
        dash.dcc.DatePickerRange(
            id='my-date-picker-range',
            min_date_allowed=datetime.date(1995, 8, 5),
            max_date_allowed=datetime.datetime.now().date(),
            initial_visible_month=datetime.datetime.now().date(),
            end_date=datetime.date(2017, 8, 25)
        ),
        dash.html.Div(id='output-container-date-picker-range')
    ]),
    layouts.get_company_reports_table(),
    layouts.get_button_to_save_db_content(),
    layouts.get_button_to_save_all_report_files_from_db_to_disk(),
]