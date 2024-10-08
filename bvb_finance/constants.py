from pathlib import Path

bvb_finance = 'bvb-finance'
financial_reports = 'financial_reports'
download_url = 'https://m.bvb.ro/'
company_financial_data_url_template = 'https://m.bvb.ro/FinancialInstruments/Details/FinancialInstrumentsDetails.aspx?s={ticker}'
company_bvb_webpage_headers = {'User-Agent': 'Mozilla/5.0'}
bvb_company_ticker_pattern = '{ticker}.RO'

portfolio_data = 'portfolio_data'
historical_prices = 'historical_prices'
portfolio_data_path = Path(__file__).parent.parent / portfolio_data
root_dir = portfolio_data_path
portfolio_historical_data_path = portfolio_data_path / historical_prices

portfolio_data_path.mkdir(mode=0o777, parents=True, exist_ok=True)
portfolio_historical_data_path.mkdir(mode=0o777, parents=True, exist_ok=True)
