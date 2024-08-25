from . import dto
import json
import os
import typing
import pathlib
import datetime
import pandas as pd
from bvb_finance import logging
from bvb_finance import constants
from bvb_finance.portfolio.trading_view import perform_data_transfomration  

logger = logging.getLogger()

root_path = pathlib.Path(__file__).parent.parent.parent
portfolio_acquisition_details = root_path / 'resources/portfolio_acquisition_details_by_date.tsv'
portfolio_stock_splits = root_path / 'resources/stock_splits.tsv'

def load_acquisitions_data(path: pathlib.Path) -> pd.DataFrame :
    if not path.exists():
        logger.warn(f'User did not specify acquisition details for his portfolios in {path.as_posix()}')
        return pd.DataFrame()
    df: pd.DataFrame = pd.read_csv(path, sep='\t', index_col=False)
    logger.info(f'Successfuly loaded portfolio acquisition data from {path.as_posix()}')
    return df

def load_stock_splits_data(path: pathlib.Path) -> pd.DataFrame :
    if not path.exists():
        logger.warn(f'User did not specify stock splits data for his portfolios in {path.as_posix()}')
        return pd.DataFrame()
    df: pd.DataFrame = pd.read_csv(path, sep='\t', index_col=False)
    logger.info(f'Successfuly loaded stock splits data from {path.as_posix()}')
    return df

def load_historical_data_single_ticker(ticker: str | pathlib.Path) -> None | pd.DataFrame:
    file = (constants.portfolio_historical_data_path / ticker).with_suffix(".csv")
    ticker = file.name.split(".")[0]
    if not file.exists():
        logger.warn(f"Falid to load historical data for ticker {ticker} File {file.as_posix()} does not exist")
        return
    logger.info(f"Loadibg historical data for {ticker}")
    df: pd.DataFrame = pd.read_csv(file, index_col=False)
    perform_data_transfomration(df)
    return df

def load_historical_data_many_tickers(tickers: list[str]) -> dto.MarketData:
    concat_df: pd.DataFrame = pd.concat([load_historical_data_single_ticker(ticker) for ticker in tickers])
    concat_df.sort_values(['date', 'symbol'], inplace=True)
    concat_df.index = list(range(len(concat_df)))
    dto.MarketData.create_data(concat_df)
    return dto.MarketData()