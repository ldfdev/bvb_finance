import requests
import typing
import chompjs
import sys
import re
import json
import datetime
from bs4 import BeautifulSoup
from http import HTTPStatus
import pandas as pd
from bvb_finance.marketcap import dto
from bvb_finance import datetime_conventions
from bvb_finance import logging

logger = logging.getLogger()

companies_by_market_cap_url = 'https://www.bvbradar.ro/lista-companiilor/'
headers = {'User-Agent': 'Mozilla/5.0'}


def download_market_cap_data() -> str:
    logger.info(f'Downloading market cap data from {companies_by_market_cap_url}')
    response = requests.get(companies_by_market_cap_url, headers=headers)

    if HTTPStatus.OK != response.status_code:
        print(f'Could not download market_cap_data from {companies_by_market_cap_url}')
        print(response.headers)
        print(response.text)
        sys.exit(-1)

    logger.info('market cap data successfully downloaded')
    return response.text

def parse_market_cap_modification_date(response: str) -> datetime.datetime:
    soup = BeautifulSoup(response, 'html.parser')
    head = soup.find('head')
    head_scripts = head.findAll('script')
    for script in head_scripts:
        dict_ = json.loads(script.text)
        # webpage format for dattime
        # "dateModified": "2024-07-09T15:23:34.000Z",
        modification_date_time_str = dict_.get('dateModified')
        modification_date_time_str = modification_date_time_str.split(".")[0]
        date_time_formatter = "%Y-%m-%dT%H:%M:%S"
        modification_date_time = datetime.datetime.strptime(modification_date_time_str, date_time_formatter)
        logger.info(f'Successfully parsed date time {modification_date_time} from market cap data')
        return modification_date_time
    logger.error(f'Failed to parse date time: HTML head Scripts: {head_scripts}')

def parse_market_cap_data(response: str) -> typing.List[dto.CompanyMarketCap]:
    regex_row_data = re.compile(r"const ROW_DATA = (.*);")
    soup = BeautifulSoup(response, 'html.parser')
    scripts = soup.findAll('script')
    market_cap_data: typing.List[dto.CompanyMarketCap] = list()
    raw_data = None
    for script in scripts:
        if data := regex_row_data.match(script.text.strip()):
            raw_data = data.group(1).rstrip(";")
            break
    market_cap_data = chompjs.parse_js_object(raw_data)
    market_cap_data = [dto.CompanyMarketCap(data) for data in market_cap_data]
    logger.info(f'Successfully parsed market cap data for {len(market_cap_data)} companies')
    return market_cap_data

def convert_market_cap_data_to_df(data: list[dto.CompanyMarketCap]) -> pd.DataFrame:
    output = list()
    for data in data:
        output_record = [
            data.simbol,
            data.nume,
            data.pret,
            data.capitalizare,
            data.var7d
        ]
        output.append(output_record)

    market_cap_df: pd.DataFrame = pd.DataFrame(output, columns=['Ticker', 'Nume', 'Pret', 'Capitalizare', "Var 7 zile"])
    return market_cap_df.to_dict('records')

def  get_market_cap_data() -> dto.MarketCapDataUiPayload:
    html_data = download_market_cap_data()
    python_data: list[dto.CompanyMarketCap] = parse_market_cap_data(html_data)
    pandas_data: pd.DataFrame = convert_market_cap_data_to_df(python_data)
    modif_datetime: datetime.datetime = parse_market_cap_modification_date(html_data)
    modif_datetime_str: str = datetime.datetime.strftime(modif_datetime, datetime_conventions.date_time_format)

    return dto.MarketCapDataUiPayload({
        'modofication_date': modif_datetime_str,
        'data': pandas_data
    })
