import dash
import bvb_finance
from bvb_finance import logging
from bvb_finance.layouts import news as news_layout

logger = logging.getLogger()
dash.register_page(__name__, name='Stock Market News', path='/news')

layout = news_layout.get_layout()
