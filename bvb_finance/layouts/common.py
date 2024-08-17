import dash
import typing
import pandas as pd
from bvb_finance.common import dto as common_dto
from bvb_finance import datetime_conventions
from bvb_finance import logging

logger = logging.getLogger()

def disable_component_till_completion(component_id: str):
    return [dash.Output(component_id=component_id, component_property='disabled'), True, False]


def get_table():
    return dash.dash_table.DataTable(
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
        sort_action="native",
        sort_mode="multi",
        sort_by=[],
        export_format="csv",
    )

def convert_dict_to_dataframe(dicts: typing.Iterable[common_dto.DictConverter]):
    columns = None
    data = list()
    count = 0
    for document in dicts:
        count += 1
        dict_ = document._dict
        if columns is None:
            columns = [key.upper() for key in dict_.keys()]
        data.append([datetime_conventions.datetime_to_string(v) for v in dict_.values()])
    report_df = pd.DataFrame(data, columns=columns)
    logger.info(f'Converted {count} items of type {dict_} to DataFrame')
    return report_df.to_dict('records')
