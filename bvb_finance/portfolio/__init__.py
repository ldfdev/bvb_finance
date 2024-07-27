import typing
import operator
import pandas as pd
from bvb_finance import logging
from bvb_finance.common import portfolio_loader
from bvb_finance.common import numeric
from bvb_finance.portfolio import dto
from bvb_finance.portfolio import loaders
from bvb_finance.portfolio.acquistions_processor import AcquisitionsProcessor

logger = logging.getLogger()

tickers = portfolio_loader.load_portfolio_tickers()

acquisitions: list[dto.Acquisition] = loaders.load_acquisitions_data(loaders.portfolio_acquisition_details)

NullableFLoat: typing.TypeVar = float | str


def compute_roi(initial_sum: NullableFLoat, final_sum: NullableFLoat) -> NullableFLoat:
    if isinstance(initial_sum, str):
        return "N/A"
    if isinstance(final_sum, str):
        return "N/A"
    return (final_sum / initial_sum - 1) * 100

def obtain_portfolio_data() -> list[dto.UIDataDict]:
    logger.info("Gathering acquisitions data")
    acquisitions_df: pd.DataFrame = loaders.load_acquisitions_data(loaders.portfolio_acquisition_details)
    acquisitions: list[dto.Acquisition] = AcquisitionsProcessor.process_acquisitions_from_dataframe(acquisitions_df)

    logger.info("Gathering stock splits data")
    stock_split_df: pd.DataFrame = loaders.load_stock_splits_data(loaders.portfolio_stock_splits)
    stock_splits: list[dto.StockSplit] = AcquisitionsProcessor.process_stock_splits_from_dataframe(stock_split_df)

    for i, a in enumerate(acquisitions, start=1):
        logger.info(f"  {i}: {a.dict}")
    logger.info("Aggregating acquisitios data")
    grouped_acquisitions: list[dto.UIPartialDataCostOfAcquisition] = AcquisitionsProcessor.group_acquisitions_data()
    for i, a in enumerate(grouped_acquisitions, start=1):
        logger.info(f"  {i}: {a}")
    
    ui_data: list[dto.UIDataDict] = list()

    logger.info("Loading market data")
    market_data: dto.MarketData = loaders.load_historical_data_many_tickers(tickers)
    for grouped_acquisition in grouped_acquisitions:
        ticker: str = grouped_acquisition["symbol"]
        invested_sum: float = grouped_acquisition["invested_sum"]
        market_value, market_value_date = "N/A", "N/A"
        data = market_data.get_market_value(ticker)
        if data:
            market_value, market_value_date = data
        compamy_market_vlue: float = numeric.safe_prod(market_value, grouped_acquisition["num_of_shares"])
        ui_data.append({
            "symbol": ticker,
            "num_of_shares": grouped_acquisition["num_of_shares"],
            "invested_sum": invested_sum,
            "market_value": compamy_market_vlue,
            "last_closing_price": market_value,
            "market_value_date": market_value_date,
            "roi": compute_roi(invested_sum, compamy_market_vlue),
        })
    return ui_data
