import datetime
import dateutil
import enum
import typing
import fractions
from decimal import Decimal
import pandas as pd
import numpy as np
from bvb_finance import logging
from bvb_finance import datetime_conventions
from bvb_finance.portfolio import dto
from bvb_finance.common import datetime as common_datetime
from bvb_finance.common import na_type
from bvb_finance.common import portfolio_loader

logger = logging.getLogger()

tickers = portfolio_loader.load_portfolio_tickers()

def get_market_data_instance():
    market_data: dto.MarketData = dto.MarketData()
    return market_data

def variation_decorator(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        variation_enum, count = args
        variation_enum_header: str = variation_enum.header.format(count)
        return VariationEnumMeta(
            variation_enum.name,
            count,
            variation_enum_header,
            variation_enum.ref_interval.format(variation_enum_header))
    return wrapper

class VariationEnum(enum.Enum):
    DAILY_VAR      = (1, "{} Day Var")
    MONTHLY_VAR    = (1, "{} Month Var")
    THIS_MONTH_VAR = (None, "This Month Var")
    YTD            = (None, "YTD Var")

    def __init__(self, count: int, header: str):
        self.count = count
        self.header = header
        self.ref_interval = "Interval {}"
    
    def __call__(self, count=None):
        """
        the decorator does not capute the default count=None arg
        it is needed to pass it explicitly
        this is why I introduced the _wrapped_call function
        """
        return self._wrapped_call(count)
    
    @variation_decorator
    def _wrapped_call(self, count):
        pass
    
    def __eq__(self, other: str) -> bool:
        return self.name == other


class VariationEnumMeta:
    def __init__(self,
                 variation_enum_name,
                 variation_enum_count,
                 variation_enum_header,
                 variation_enum_ref_interval):
        self.name = variation_enum_name
        self.count = variation_enum_count
        self.header = variation_enum_header
        self.ref_interval = variation_enum_ref_interval
    
    def get_start_date(self, ref_date: datetime.date) -> datetime.date:
        if VariationEnum.DAILY_VAR == self.name:
            return self._diff_in_days(ref_date)
        if VariationEnum.MONTHLY_VAR == self.name:
            return self._diff_in_months(ref_date)
        if VariationEnum.THIS_MONTH_VAR == self.name:
            return self._diff_this_month(ref_date)
        if VariationEnum.YTD == self.name:
            return self._diff_ytd(ref_date)
        raise NotImplementedError
    
    def _diff_in_days(self, ref_date: datetime.date) -> datetime.date:
        dt = datetime.datetime(year=ref_date.year, month=ref_date.month, day=ref_date.day) - datetime.timedelta(days=self.count)
        return dt.date()
    
    def _diff_in_months(self, ref_date: datetime.date) -> datetime.date:
        return ref_date - dateutil.relativedelta.relativedelta(months=self.count)
    
    def _diff_this_month(self, ref_date: datetime.date) -> datetime.date:
        dt = datetime.datetime(year=ref_date.year, month=ref_date.month, day=1)
        # if dt is Saturday the 3rd date will be business day
        return common_datetime.get_bussiness_days_starting_at(dt, 3)[0]
    
    def _diff_ytd(self, ref_date: datetime.date) -> datetime.date:
        dt = datetime.datetime(year=ref_date.year, month=1, day=1)
        # Assuming Jan 1, Jan 2 stock exchange is closed we use a buffer of 5 days
        first_business_day_in_year: datetime.date = common_datetime.get_bussiness_days_starting_at(dt, 5)[0]
        return first_business_day_in_year
    
    def __repr__(self):
        cls = self.__class__.__name__
        attrs = ', '.join(f'{key}={value!r}' for key, value in self.__dict__.items())
        return f'{cls}({attrs})'


def build_tickers_variations_data(*variations: typing.Iterable[VariationEnumMeta]) -> pd.DataFrame:
    market_data: pd.DataFrame = get_market_data_instance()
    tickers: list[str] = just_unique_values(market_data.df['symbol'])
    df: pd.DataFrame = pd.DataFrame()
    for variation in variations:
        variation_df: pd.DataFrame = create_tickers_variation_dataframe(tickers, variation)
        for column in list(variation_df.columns):
            # only the symbol column is overwritten
            # but create_tickers_variation_dataframe creates teh same symbol column
            # this is the only column that is non unique
            df[column] = variation_df[column]
    return df

def create_tickers_variation_dataframe(tickers: list[str], variation: VariationEnumMeta) -> pd.DataFrame:
    column_label: str = variation.header
    df: pd.DataFrame = pd.DataFrame()
    df['symbol'] = tickers
    variation_data = [build_ticker_variation(ticker, variation) for ticker in df['symbol']]
    logger.info(f"variation_data {variation_data}. tickers {tickers}")
    variation_column = [vd[0] for vd in variation_data]
    variation_date_ranges = ["{} - {}".format(
        datetime_conventions.datetime_to_string(start_date),
        datetime_conventions.datetime_to_string(end_date))
        for _, [start_date, end_date] in variation_data
    ]
    df[column_label] = variation_column
    df[variation.ref_interval] = variation_date_ranges
    return df

def build_ticker_variation(ticker: str, variation: VariationEnumMeta):
    '''
    returns na_type.NAType if variation data cannot be computed from dataframe data
    '''
    logger.info(f"build_ticker_variation({ticker}, {variation})")
    market_data: pd.DataFrame = get_market_data_instance()
    null_response = na_type.NAType, [na_type.NAType, na_type.NAType]
    ticker_data: dto.MarketData = dto.MarketData(market_data.get_ticker_df(ticker))
    dates: list[datetime.date] = ticker_data.get_dates()
    if not dates:
        logger.warning(f"Ticker {ticker} no 'date' in market_data dataframe")
        return null_response
    newest_date: datetime.date = dates[-1]
    start_date: datetime.date = variation.get_start_date(ref_date=newest_date)

    prices_df: pd.DataFrame = ticker_data.find_dates_in_range(start_date, newest_date)
    
    if len(prices_df) < 2:
        logger.warning(f"Ticker {ticker} Less than 2 values in market_data dataframe")
        return na_type.NAType, [start_date, newest_date]
    
    prices_df_start_date: datetime.date = prices_df.iloc[0]['date']
    if (start_date != prices_df_start_date):
        logger.warning(f"Ticker {ticker}  market_data dataframe start date is {prices_df_start_date}. Expected {start_date}")
        if VariationEnum.YTD != variation.name:
            return na_type.NAType, [start_date, newest_date]
        logger.warning(f"Ticker {ticker}. Detected {variation.name} variation. will use start_date {prices_df_start_date} instead of {start_date}")
        start_date = prices_df_start_date
    
    prices: list[float] = list(prices_df['close'])
    first_price, last_price = prices[0], prices[-1]
    first_fraction = fractions.Fraction(first_price)
    last_fraction = fractions.Fraction(last_price)
    l1, l2 = last_fraction.numerator, last_fraction.denominator
    f1, f2 = first_fraction.numerator, first_fraction.denominator
    result = fractions.Fraction(100 * (l1*f2-l2*f1), l2*f1)
    return float(result), [start_date, newest_date]

def build_portfolio_variations_data() -> pd.DataFrame:
    market_data: pd.DataFrame = get_market_data_instance()

    df: pd.DataFrame = pd.DataFrame()
    
    # last 24 hrs
    newest: pd.DataFrame = market_data.df.iloc[-2:]
    last_2_days: list[datetime.date] = list(newest['date'])
    last_2_bussiness_days: list[datetime.date] = common_datetime.get_bussiness_days_starting_at(last_2_days[0], 2)
    if last_2_days == last_2_bussiness_days:
        # "1 Day Var"
        # TODO
        # scan market_data for all symbols and verify last 2 bussiness days exists for each symbol
        # only then computed the variations
        pass
    else:
        logger.warning(f"MarketData df\n" +
                    f"{market_data.df.iloc[-3:]}\n" +
                    f"does not contain data for last 2 consecutive bussiness days" +
                    f"Skipping collecting 1 day variations")
        
    return df

def timedelta_in_days(dates: list[datetime.date]) -> int:
    '''
    returns the timedelta in days between the first and the last dates in parameter dates
    '''
    first, last = dates[0], dates[-1]
    td: datetime.timedelta = last - first
    return td.days

def just_unique_values(s: pd.Series) -> list[typing.Any]:
    uniques = []
    visited = set()
    for s in s:
        if s in visited:
            continue
        visited.add(s)
        uniques.append(s)
    return uniques