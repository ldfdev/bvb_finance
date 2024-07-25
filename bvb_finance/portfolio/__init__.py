import typing
import operator
from bvb_finance import logging
from bvb_finance.common import portfolio_loader
from bvb_finance.common import numeric
from bvb_finance.portfolio import dto
from bvb_finance.portfolio import loaders

logger = logging.getLogger()

tickers = portfolio_loader.load_portfolio_tickers()

acquisitions: list[dto.Acquisition] = loaders.load_acquisitions_data(loaders.portfolio_acquisition_details)

NullableFLoat: typing.TypeVar = float | str

class UIPartialDataCostOfAcquisition(typing.TypedDict):
    symbol: str
    invested_sum: float
    num_of_shares: int
    fees: float

def compute_roi(initial_sum: NullableFLoat, final_sum: NullableFLoat) -> NullableFLoat:
    if isinstance(initial_sum, str):
        return "N/A"
    if isinstance(final_sum, str):
        return "N/A"
    return (final_sum / initial_sum - 1) * 100

def obtain_portfolio_data() -> list[dto.UIDataDict]:
    logger.info("Gathering acquisitions data")
    acquisition: list[dto.Acquisition] = loaders.load_acquisitions_data(loaders.portfolio_acquisition_details)
    for i, a in enumerate(acquisitions, start=1):
        logger.info(f"  {i}: {a.dict}")
    logger.info("Aggregating acquisitios data")
    lst: list[UIPartialDataCostOfAcquisition] = group_acquisitions_data(acquisition)
    for i, a in enumerate(lst, start=1):
        logger.info(f"  {i}: {a}")
    
    ui_data: list[dto.UIDataDict] = list()

    logger.info("Loading market data")
    market_data: dto.MarketData = loaders.load_historical_data_many_tickers(tickers)
    for l in lst:
        ticker: str = l["symbol"]
        invested_sum: float = l["invested_sum"]
        market_value, market_value_date = "N/A", "N/A"
        data = market_data.get_market_value(ticker)
        if data:
            market_value, market_value_date = data
        compamy_market_vlue: float = numeric.safe_prod(market_value, l["num_of_shares"])
        ui_data.append({
            "symbol": ticker,
            "num_of_shares": l["num_of_shares"],
            "invested_sum": invested_sum,
            "market_value": compamy_market_vlue,
            "last_closing_price": market_value,
            "market_value_date": market_value_date,
            "roi": compute_roi(invested_sum, compamy_market_vlue),
        })
    return ui_data

def group_acquisitions_data(acquisitions: list[dto.Acquisition]) -> list[UIPartialDataCostOfAcquisition]:
    visited: typing.Dict[str, UIPartialDataCostOfAcquisition] = dict()
    for acquisition in acquisitions:
        cache: typing.Optional[dto.Acquisition] = visited.get(acquisition.symbol) 
        if cache is None:
            cache = {
                "symbol": acquisition.symbol,
                "invested_sum": 0.0,
                "num_of_shares": 0,
                "fees": 0.0
            }
            visited[acquisition.symbol] = cache

        cache["num_of_shares"] += acquisition.quantity
        cache["invested_sum"] += acquisition.price
        cache["fees"] += acquisition.fees
    result = [v for v in visited.values()]
    logger.info(f"Constructed grouped acquisitions data: {result}")
    result.sort(key = lambda d: d["symbol"])
    return result

