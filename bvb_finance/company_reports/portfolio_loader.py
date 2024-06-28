import json
import pathlib
import logging

logger = logging.getLogger(__name__)

portfolio_companies = 'resources/portfolio_companies.json'

def load_portfolio_tickers() -> list[str]:
    path = pathlib.Path(__file__).parent.parent / portfolio_companies
    if not path.exists():
        logger.warn(f'User did not specify a portfolio of company tickers in {portfolio_companies}')
        return []
    with open(path) as reader:
        return json.load(reader)
