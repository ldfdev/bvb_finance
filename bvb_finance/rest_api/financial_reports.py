from bvb_finance.common import portfolio_loader

def get_portfolio_tickrs() -> list[str]:
    return portfolio_loader.load_portfolio_tickers()