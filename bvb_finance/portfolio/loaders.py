from . import dto
import json
import os
import typing
import pathlib
import datetime
import pandas as pd
from bvb_finance import logging
from bvb_finance import constants
from tvDatafeed import TvDatafeed, Interval

logger = logging.getLogger()

root_path = pathlib.Path(__file__).parent.parent.parent
portfolio_acquisition_details = root_path / 'resources/portfolio_acquisition_details_by_date.tsv'
portfolio_stock_splits = root_path / 'resources/stock_splits.tsv'

TradingViev = TvDatafeed()
TRADINGVIEW_BVB_SYMBOL='BVB'

constants.portfolio_data_path.mkdir(mode=0o777, parents=True, exist_ok=True)
constants.portfolio_historical_data_path.mkdir(mode=0o777, parents=True, exist_ok=True)

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

def perfomr_data_transfomration(df: pd.DataFrame):
    columns = list(df.columns)
    if 'datetime' not in columns:
        return
    logger.info("Performing data transformation for columns [datetime, symbol]")
    df['datetime'] = df['datetime'].apply(dto.HistoricalData.convert_date_from_str)
    df['symbol'] = df['symbol'].apply(dto.HistoricalData.convert_symbol_from_trading_view_format)
    df.rename(columns={'datetime': 'date'}, inplace=True)

def download_historical_data_single_ticker(ticker: str) -> pd.DataFrame:
    file = (constants.portfolio_historical_data_path / ticker).with_suffix(".csv")
    if file.exists():
        logger.warn(f"Skipping downloading historical data for {ticker}. Already exists: {file.as_posix()}")
        return pd.read_csv(file, index_col=False)
    
    logger.info(f"Getting trading view data for ticker {ticker}")
    df: pd.DataFrame = TradingViev.get_hist(
        symbol=ticker,
        exchange=TRADINGVIEW_BVB_SYMBOL,
        interval=Interval.in_weekly,
        n_bars=500)
    if df is None:
        logger.warn(f"Failed to download trading view data for {ticker}")
        return pd.DataFrame()
    df.reset_index(inplace=True)

    perfomr_data_transfomration(df)
    
    logger.info(f"Saving dataframe to {file.as_posix()}")
    df.to_csv(file, index=False)
    return df

def download_historical_data(tickers: list[str]):
    for ticker in tickers:
        download_historical_data_single_ticker(ticker)

def load_historical_data_single_ticker(ticker: str | pathlib.Path) -> None | pd.DataFrame:
    file = (constants.portfolio_historical_data_path / ticker).with_suffix(".csv")
    ticker = file.name.split(".")[0]
    if not file.exists():
        logger.warn(f"Falid to load historical data for ticker {ticker} File {file.as_posix()} does not exist")
        return
    logger.info(f"Loadibg historical data for {ticker}")
    df: pd.DataFrame = pd.read_csv(file, index_col=False)
    perfomr_data_transfomration(df)
    return df

def load_historical_data_many_tickers(tickers: list[str]) -> dto.MarketData:
    concat_df: pd.DataFrame = pd.concat([load_historical_data_single_ticker(ticker) for ticker in tickers])
    concat_df.sort_values(['date', 'symbol'], inplace=True)
    concat_df.index = list(range(len(concat_df)))
    dto.MarketData.create_data(concat_df)
    return dto.MarketData()