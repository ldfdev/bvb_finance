import json
import pathlib
from bvb_finance import logging

logger = logging.getLogger()

portfolio_companies = 'resources/portfolio_companies.json'

def load_portfolio_tickers() -> list[str]:
    path = pathlib.Path(__file__).parent.parent.parent / portfolio_companies
    if not path.exists():
        logger.warn(f'User did not specify a portfolio of company tickers in {portfolio_companies}')
        return []
    with open(path) as reader:
        return json.load(reader)
