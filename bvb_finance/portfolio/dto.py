import datetime
import numbers
import typing
import json
import dataclasses
import operator
import re
import bisect
import pandas as pd
from bvb_finance import datetime_conventions
from bvb_finance import logging

logger = logging.getLogger()

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        if isinstance(o, datetime.date):
            return o.strftime(datetime_conventions.date_format)
        if isinstance(o, datetime.time):
            return o.strftime(datetime_conventions.time_format)
        return super().default(o)
                              
class DictConverter:
    def __init__(self, d: typing.Dict):
        self._dict = d

    @property
    def dict(self):
        return self._dict
    
    def __getattr__(self, name):
        return self._dict.get(name)

    def __str__(self):
        return json.dumps(self._dict, cls=JSONEncoder, indent=4)

class AcquisitionDict(typing.TypedDict):
    date: datetime.date
    symbol: str
    quantity: int
    price: float
    fees: float

class Acquisition(DictConverter):
    @staticmethod
    def convert_price_to_float(value: str | numbers.Number) -> float:
        if isinstance(value, numbers.Number):
            return float(value)
        return float(value.replace(",", ""))

    @staticmethod
    def convert_date_from_str(value: str | datetime.date) -> datetime.date:
        if isinstance(value, datetime.date):
            return value
        return datetime.datetime.strptime(value, datetime_conventions.date_format).date()

    def __init__(self, d: AcquisitionDict):
        d_copy = {k: v for k, v in d.items()}
        d_copy['price'] = self.convert_price_to_float(d_copy.get('price'))
        d_copy['date'] = self.convert_date_from_str(d_copy['date'])
        super().__init__(d_copy)


class HistoricalDataDict(typing.TypedDict):
    date: datetime.date
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: int

class HistoricalData(DictConverter):
    @staticmethod
    def convert_date_from_str(value: str | datetime.date) -> datetime.date:
        if isinstance(value, datetime.date):
            return value
        return datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S").date()

    @staticmethod
    def convert_symbol_from_trading_view_format(symbol: str) -> str:
        trading_view_symbol_format = "BVB:(\\w+)"
        pattern: re.Pattern = re.compile(trading_view_symbol_format)
        return pattern.match(symbol).group(1)


class PortfolioDict(typing.TypedDict):
    market_value: float
    acquisition_price: float

class MarketData:
    df: pd.DataFrame

    @classmethod
    def create_data(cls, data: pd.DataFrame):
        cls.df = data
    
    def get_dates(self) -> list[datetime.date]:
        return list(self.df['date'])

    def find_closest_date(self, date: datetime.date) -> datetime.date:
        '''
        finds date that is as close as possible from date , not greater than date
        '''
        dates = self.get_dates()
        pos = bisect.bisect_left(dates, date)
        # logger.info(f"Bisecting {dates} for {date} gives {pos}")
        if pos >= len(dates):
            # return a smaller dates since the serahced for is not available
            return dates[-1]
        if dates[pos] > date:
            if pos == 0:
                return
            return dates[pos - 1]
        result = dates[pos]
        if (pos + 1 < len(dates)) and (dates[pos + 1] == date):
            result = dates[pos + 1]
        return result

    def get_newest_date(self) -> datetime.date:
        return self.get_dates()[-1]

    def get_market_value(self, ticker: str, date: datetime.date = None) -> typing.Tuple[float, datetime.date]:
        chosen_date = self.get_newest_date() if date is None else self.find_closest_date(date)
        market_value_df: pd.DataFrame = self.df.loc[(self.df['symbol'] == ticker) & (self.df['date'] == chosen_date), :]
        logger.info(f"Market value for {ticker} at {chosen_date} is {market_value_df} [closing price]")
        if len(market_value_df) == 0:
            return
        first_item_index = list(market_value_df.index)[0]
        return (market_value_df.loc[first_item_index, "close"],
                market_value_df.loc[first_item_index, "date"],)

class Portfolio:
    def __init__(self, acquisitions: list[Acquisition]):
        self.acquisitions = sorted(acquisitions, key=operator.attrgetter('date', 'symbol', 'quantity'))

    @staticmethod
    def construct_from_sorted(acquisitions: list[Acquisition]) -> 'Portfolio':
        p = Portfolio(list())
        p.acquisitions = acquisitions
        return p
    
    def get_at_date(self, date: datetime.date) -> 'Portfolio':
        return Portfolio.construct_from_sorted([
            a for a in self.acquisitions if a.date <= date
        ])
    
    def get_acquisition_price(self, include_fees: bool = False) -> float:
        s: float = sum(a.quantity * a.price for a in self.acquisitions)
        if include_fees:
            s += self.get_acquisition_fees()
        return s
    
    def get_acquisition_fees(self) -> float:
        return sum(a.fees for a in self.acquisitions)

class UIDataDict(typing.TypedDict):
    symbol: str
    num_of_shares: int
    invested_sum: float
    market_value: float
    last_closing_price: float
    market_value_date: datetime.date
    roi: float
    price_var_1w: float
    price_var_1m: float
    price_var_3m: float
