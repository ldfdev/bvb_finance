import datetime
import enum
import typing
import fractions
from decimal import Decimal
import pandas as pd
import numpy as np
from bvb_finance import logging
from bvb_finance.portfolio import dto
from bvb_finance.common import datetime as common_datetime
from bvb_finance import portfolio

logger = logging.getLogger()

tickers = portfolio.tickers
market_data: dto.MarketData = dto.MarketData()

class VariationEnum(enum.Enum):
    VAR_1_DAY  = (1, "1 Day Var")
    VAR_7_DAYS = (7, "7 Day Var")
    VAR_28_DAYS = (28, "28 Day Var")
    VAR_MONTH_TO_DATE = (None, "Month To Date Var")

def build_tickers_variations_data(variation: VariationEnum) -> pd.DataFrame:
    tickers = market_data.df['symbol']
    days_count, column_label = variation.value
    df: pd.DataFrame = pd.DataFrame()
    df['symbol'] = just_unique_values(market_data.df['symbol'])
    one_day_var = [build_ticker_variation(ticker, days_count) for ticker in df['symbol']]
    df[column_label] = one_day_var
    
    return df

def build_ticker_variation(ticker: str, variation_in_days: int):
    '''
    returns np.nan if variation data cannot be computed from dataframe data
    '''
    logger.info(f"build_ticker_variation({ticker}, {variation_in_days})")
    n = variation_in_days + 1
    ticker_data: pd.DataFrame = market_data.df.loc[(market_data.df['symbol'] == ticker), :]
    dates: list[datetime.date] = list(ticker_data.loc[:, 'date'])
    if not dates:
        return np.nan
    # build n days variation where n = variation_in_days
    
    # scanning most recent n dates
    # this is because we colelct data weekly or daily
    candidate_dates = dates[-n:]
    logger.info(f"Candidate dates = {candidate_dates}")
    for index, candidate in enumerate(candidate_dates, start=-n):
        logger.info( f"Timedelta between {candidate} and {candidate_dates[-1]} " +\
                    f"is {timedelta_in_days([candidate, candidate_dates[-1]])} " +\
                    f"expected {n - 1}")
        if timedelta_in_days([candidate, candidate_dates[-1]]) == n - 1:
            prices: list[float] = list(ticker_data.iloc[index:, :]['close'])
            first_price, last_price = prices
            first_fraction = fractions.Fraction(first_price)
            last_fraction = fractions.Fraction(last_price)
            l1, l2 = last_fraction.numerator, last_fraction.denominator
            f1, f2 = first_fraction.numerator, first_fraction.denominator
            result = fractions.Fraction(100 * (l1*f2-l2*f1), l2*f1)
            return float(result)
    return np.nan

def build_portfolio_variations_data() -> pd.DataFrame:
    market_data: dto.MarketData = dto.MarketData()

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