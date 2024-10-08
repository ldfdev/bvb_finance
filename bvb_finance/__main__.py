import dash
import dotenv
import logging
import typing
from bvb_finance import logging
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from . import containers
from bvb_finance.rest_api import portfolio as rest_api_portfolio
import bvb_finance
from bvb_finance.common import network_utils

env_config = dotenv.dotenv_values()

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

@flask_server.route("/api/portfolio/tickers/", methods=['GET'])
def get_portfolio_tickers():
    logger.info("Serving GET /api/portfolio/tickers")
    return rest_api_portfolio.get_portfolio_tickers()

@flask_server.route("/api/portfolio/acquisitions/", methods=['GET'])
def get_acquisitions_data():
    logger.info("Serving GET /api/portfolio/acquisitions")
    return rest_api_portfolio.get_acquisitions_data_as_json()

# Run the app
if __name__ == '__main__':
    logger.info("==================================")
    logger.info("===== DASH APP INITIALIZED =======")
    logger.info("==================================")

    containers.start_mongo_container()

    # app.run(debug=True)

    ips_map: dict[str, str] = network_utils.get_local_interfaces()
    ip: typing.Optional[str] = ips_map.get(env_config.get("INTERFACE_FOR_FLASK_SERVER"))
    if ip is None:
        ip = "localhost"
    port: int = 8050
    logger.info(f"Starting Flask Server on {ip}:{port}")
    bvb_finance.flask_server.run(host=ip, port=8050, debug=True)