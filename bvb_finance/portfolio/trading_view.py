import datetime
import pandas as pd
import typing
import concurrent.futures
from pathlib import Path
from bvb_finance import logging
from bvb_finance import constants
from bvb_finance.portfolio import dto
from tvDatafeed import TvDatafeed, Interval

logger = logging.getLogger()

TradingViev = TvDatafeed()
TRADINGVIEW_BVB_SYMBOL='BVB'

def perform_data_transfomration(df: pd.DataFrame):
    columns = list(df.columns)
    if 'datetime' in columns:
        logger.info("Performing data transformation for columns [datetime, symbol]")
        df['datetime'] = df['datetime'].apply(dto.HistoricalData.convert_date_from_str)
        df['symbol'] = df['symbol'].apply(dto.HistoricalData.convert_symbol_from_trading_view_format)
        df.rename(columns={'datetime': 'date'}, inplace=True)
    else:
        # if date is saved as str convert it to datetime.date
        df['date'] = df['date'].apply(dto.HistoricalData.convert_date_from_str)

def download_trading_view_data(ticker: str) -> pd.DataFrame:
    df: pd.DataFrame = TradingViev.get_hist(
        symbol=ticker,
        exchange=TRADINGVIEW_BVB_SYMBOL,
        interval=Interval.in_weekly,
        n_bars=500)
    if df is None:
        logger.warn(f"Failed to download trading view data for {ticker}")
        return pd.DataFrame()
    df.reset_index(inplace=True)
    return df

def get_portfolio_historical_data_csv(ticker: str) -> Path:
    return (constants.portfolio_historical_data_path / ticker).with_suffix(".csv")

def download_historical_data_single_ticker(ticker: str) -> pd.DataFrame:
    file = get_portfolio_historical_data_csv(ticker)
    if file.exists():
        logger.warn(f"Skipping downloading historical data for {ticker}. Already exists: {file.as_posix()}")
        return pd.read_csv(file, index_col=False)
    
    logger.info(f"Getting trading view data for ticker {ticker}")

    df = download_trading_view_data(ticker)
    perform_data_transfomration(df)
    
    logger.info(f"Saving dataframe to {file.as_posix()}")
    df.to_csv(file, index=False)
    return df

def is_sorted_by_date(date_list: list[datetime.date]) -> bool:
    if len(date_list) == 0:
        return True
    if not isinstance(date_list[0], datetime.date):
        logger.warm(f"Expected datetime.date in list data. but was {type(date_list[0])}: list data {date_list}")
        return False
    sorted_date_list = sorted(date_list)
    return sorted_date_list == date_list

def merge_dataframes(first: pd.DataFrame, second: pd.DataFrame) -> pd.DataFrame:
    if first.empty:
        return second
    if second.empty:
        return first
    first_columns = list(first.columns)
    second_columns = list(second.columns)
    if first_columns != second_columns:
        logger.warn(f'Cannot merge dataframe with columns {first_columns} with dataframe with diferent columns {second_columns}')
        return
    first_timestamps = list(first['date'])
    second_timestamps = list(second['date'])
    new_dates = [s for s in second_timestamps if s not in first_timestamps]

    filtered_df = second.loc[second['date'].apply(lambda x: x in new_dates), :]
    result: pd.DataFrame = pd.concat([first, filtered_df])
    result.sort_values(by=['date'], inplace=True)
    result.reset_index(drop=True, inplace=True)
    return result

def show_brief(dataframe: pd.DataFrame) -> pd.DataFrame:
    brief_df = dataframe
    n = len(dataframe)
    if n >= 4:
        last = n - 1
        brief_df = dataframe.loc[[0, 1, last - 1, last]]
    logger.info(brief_df)
    # logger.info(f"DateTime type {brief_df.loc[0]['date']} = {type(brief_df.loc[0]['date'])}")
        
def download_and_merge_if_exists_historical_data_single_ticker(ticker: str) -> pd.DataFrame:
    new_df: pd.DataFrame = download_trading_view_data(ticker)
    if new_df.empty:
        logger.warn(f"download_and_merge operation failed for ticker {ticker}: Failed to download Trading View data")
        return new_df
    perform_data_transfomration(new_df)
    
    logger.info("Downloaded dataframe")
    show_brief(new_df)
    
    file = get_portfolio_historical_data_csv(ticker)
    existing_df = pd.DataFrame()
    if file.exists():
        existing_df = pd.read_csv(file, index_col=False)
        perform_data_transfomration(existing_df)
    
    logger.info("Existing dataframe")
    show_brief(existing_df)
    
    df = merge_dataframes(new_df, existing_df)
    
    logger.info(f"Saving dataframe to {file.as_posix()}")
    df.to_csv(file, index=False)
    return df

def download_historical_data(tickers: list[str]):
    for ticker in tickers:
        download_historical_data_single_ticker(ticker)

def worker_fun(ticker: str) -> typing.Optional[str]:
    """
    if download fails for ticker then tocker is returned
    Otherwise None is returned
    """
    dataframe: pd.DataFrame = download_and_merge_if_exists_historical_data_single_ticker(ticker)
    if dataframe.empty:
        return ticker
    
def download_and_merge_historical_data(tickers: list[str]) -> list[str]:
    failed_tickers: list[str] = list()
    # if the num of workers is 10 we get 429 too many requests error status code
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
    
    futures: dict[concurrent.futures.Future, str] = {
        executor.submit(worker_fun, ticker): ticker for ticker in tickers
    }
    for future in concurrent.futures.as_completed(futures):
        try:
            result = future.result()
            if result:
                failed_tickers.append(result)
        except Exception as exc:
            ticker: str = futures.get(future)
            logger.error(f"Failed to download Trading view data for ticker {ticker}", exc)
            failed_tickers.append(ticker)
    
    if len(failed_tickers) > 0:
        logger.warn(f"download_and_merge_historical_data. Failed to download new data for tickers {failed_tickers}")
    return failed_tickers

