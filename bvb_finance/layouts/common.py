import dash

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
