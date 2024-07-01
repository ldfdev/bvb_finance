import logging.handlers
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import logging
import datetime
from . import datetime_conventions
from .company_reports.BVB_Report import BVB_Report
from .company_reports import constants
from . import layouts
from .company_reports.dto import BVB_Report_Dto, Document_Dto
from . import containers
import bvb_finance

# Initialize the app
app = bvb_finance.app

logger = bvb_finance.getLogger()

logger_name = f'{constants.bvb_finance}-application'
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.handlers.RotatingFileHandler(f'{logger_name}.log', maxBytes=120 * 1024 * 1024, backupCount=2)
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
# # add the handlers to logger
# logger.addHandler(ch)
# logger.addHandler(fh)


# Incorporate data
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')

def load_local_report():
    reports = BVB_Report.load_reports_from_local()
    data = list()
    for report in reports:
        for doc in report.documents:
            line = [report.ticker, doc.file_name, doc.modification_date.strftime(datetime_conventions.date_dormat)]
            data.append(line)
    report_df = pd.DataFrame(data, columns=['Ticker', 'Report', 'Raport Date'])
    logger.debug(report_df)
    return report_df.to_dict('records')



# App layout
app.layout = [
    html.Div(children='My First App with Data'),
    html.Hr(),
    layouts.get_company_tickers_layout(),
    layouts.get_radio_bar_to_search_for_company_reports(),
    layouts.get_component_to_load_db_snapshot(),
    html.Div([
        dcc.DatePickerRange(
            id='my-date-picker-range',
            min_date_allowed=datetime.date(1995, 8, 5),
            max_date_allowed=datetime.datetime.now().date(),
            initial_visible_month=datetime.datetime.now().date(),
            end_date=datetime.date(2017, 8, 25)
        ),
        html.Div(id='output-container-date-picker-range')
    ]),
    layouts.get_table(),
    layouts.get_button_to_save_db_content(),
]

# Run the app
if __name__ == '__main__':
    logger.info("==================================")
    logger.info("===== DASH APP INITIALIZED =======")
    logger.info("==================================")

    containers.start_mongo_container()
    app.server.logger.addHandler(fh)
    app.server.logger.addHandler(ch)
        
    app.run(debug=True)