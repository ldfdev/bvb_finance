import dash
import logging
from bvb_finance import logging
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from . import containers
from bvb_finance.rest_api import financial_reports
import bvb_finance

# Initialize the app
dashApp = bvb_finance.app

logger = logging.getLogger()
flask_server = bvb_finance.flask_server

dashApp.layout = dash.html.Div([
    dash.html.H1('Multi-page app with Dash Pages'),
    dash.html.Div([
        dash.html.Div(
            dash.dcc.Link(f"{page['name']} - {page['path']}", href=page["relative_path"])
        ) for page in dash.page_registry.values()
    ]),
    dash.page_container
])

@flask_server.route("/api/financial_reports/portfolio_tickers/", methods=['GET'])
def get_portfolio_tickrs():
    logger.info("Serving GET /api/financial_reports/portfolio_tickers")
    return financial_reports.get_portfolio_tickrs()


# Run the app
if __name__ == '__main__':
    logger.info("==================================")
    logger.info("===== DASH APP INITIALIZED =======")
    logger.info("==================================")

    containers.start_mongo_container()

    # app.run(debug=True)

    logger.info("Starting Flask Server")
    bvb_finance.flask_server.run(port=8050, debug=True)