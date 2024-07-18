import requests
import typing
import chompjs
import sys
import re
from bs4 import BeautifulSoup
from http import HTTPStatus
from bvb_finance.marketcap import dto

companies_by_market_cap_url = 'https://www.bvbradar.ro/lista-companiilor/'
headers = {'User-Agent': 'Mozilla/5.0'}

def download_market_cap_data() -> requests.Response:
    response = requests.get(companies_by_market_cap_url, headers=headers)

    if HTTPStatus.OK != response.status_code:
        print(f'Could not download market_cap_data from {companies_by_market_cap_url}')
        print(response.headers)
        print(response.text)
        sys.exit(-1)

    return response.text

def parse_market_cap_data(response: str) -> typing.List[dto.CompanyMarketCap]:
    regex_row_data = re.compile(r"const ROW_DATA = (.*);")
    soup = BeautifulSoup(response, 'html.parser')
    scripts = soup.findAll('script')
    market_cap_data: typing.List[dto.CompanyMarketCap] = list()
    for script in scripts:
        if data := regex_row_data.match(script.text.strip()):
            raw_data = data.group(1).rstrip(";")
            break
    market_cap_data = chompjs.parse_js_object(raw_data)
    market_cap_data = [dto.CompanyMarketCap(data) for data in market_cap_data]
    return market_cap_data