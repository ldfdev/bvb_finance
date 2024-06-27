from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px

import datetime
from . import datetime_conventions
from .company_reports.BVB_Report import BVB_Report
from . import layouts
from .company_reports.dto import BVB_Report_Dto, Document_Dto
from . import containers

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
    print(report_df)
    return report_df.to_dict('records')

# Initialize the app
app = Dash()

# App layout
app.layout = [
    html.Div(children='My First App with Data'),
    html.Hr(),
    layouts.get_company_tickers_layout(),
    layouts.get_radio_button_to_search_for_company_reports(),
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
    dash_table.DataTable(
        id='company-reports-table',
        data=[],
        page_size=10,
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
                'backgroundColor': 'rgb(220, 220, 220)',
                'color': 'black'
            }
        ],
    ),
    layouts.get_button_to_save_db_content(),
]

# Run the app
if __name__ == '__main__':
    containers.start_mongo_container()
    app.run(debug=True)