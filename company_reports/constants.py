from pathlib import Path

root_dir = Path('/home/loxor/Documents/Programming/Python/stocks')
financial_reports = 'financial_reports'
download_url = 'https://m.bvb.ro/'
company_financial_data_url_template = 'https://m.bvb.ro/FinancialInstruments/Details/FinancialInstrumentsDetails.aspx?s={ticker}'
company_bvb_webpage_headers = {'User-Agent': 'Mozilla/5.0'}
bvb_company_ticker_pattern = '{ticker}.RO'