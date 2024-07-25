import dash
import bvb_finance
from bvb_finance import logging
from bvb_finance.layouts import portfolio as portfolio_layout

logger = logging.getLogger()
dash.register_page(__name__, name='Portfolio Evolution', path='/portfolio')

layout = portfolio_layout.get_layout()
