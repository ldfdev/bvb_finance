import logging
import dash
from bvb_finance import constants

__all__ = [
    'getLogger'
]

logger = dash.get_app().server.logger

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

logger.addHandler(fh)
# log lines are duplicate if ch is not commented
# logger.addHandler(ch)

def getLogger():
    return logger