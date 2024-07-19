import dash
import logging
from bvb_finance import logging
from . import containers
import bvb_finance

# Initialize the app
app = bvb_finance.app

logger = logging.getLogger()

app.layout = dash.html.Div([
    dash.html.H1('Multi-page app with Dash Pages'),
    dash.html.Div([
        dash.html.Div(
            dash.dcc.Link(f"{page['name']} - {page['path']}", href=page["relative_path"])
        ) for page in dash.page_registry.values()
    ]),
    dash.page_container
])

# Run the app
if __name__ == '__main__':
    logger.info("==================================")
    logger.info("===== DASH APP INITIALIZED =======")
    logger.info("==================================")

    containers.start_mongo_container()

    app.run(debug=True)