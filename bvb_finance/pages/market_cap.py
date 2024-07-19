import dash
import bvb_finance
from bvb_finance import logging
from bvb_finance.layouts import market_cap as market_cap_layout

logger = logging.getLogger()
dash.register_page(__name__, path='/market_cap')

layout = market_cap_layout.get_layout()
