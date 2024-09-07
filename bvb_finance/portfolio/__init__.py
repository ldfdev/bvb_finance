import typing
import operator
import plotly
import numpy as np
import plotly.express as px
import pandas as pd
from bvb_finance import logging
from bvb_finance.common import na_type
from bvb_finance.common import portfolio_loader
from bvb_finance.common import numeric
from bvb_finance.portfolio import dto
from bvb_finance.portfolio import loaders
from bvb_finance.portfolio.acquistions_processor import AcquisitionsProcessor
from bvb_finance.rest_api import portfolio as rest_api_portfolio 

logger = logging.getLogger()

tickers = portfolio_loader.load_portfolio_tickers()

acquisitions: list[dto.Acquisition] = loaders.load_acquisitions_data(loaders.portfolio_acquisition_details)

NullableFLoat: typing.TypeVar = float | str

@na_type.na_type_check
def compute_roi(initial_sum: NullableFLoat, final_sum: NullableFLoat) -> NullableFLoat:
    return (final_sum / initial_sum - 1) * 100

def obtain_portfolio_data() -> list[dto.UIDataDict]:
    logger.info("Gathering acquisitions data")
    acquisitions: list[dto.Acquisition] = rest_api_portfolio.get_acquisitions_data()

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

Figure = plotly.graph_objs._figure.Figure

def build_portfoloio_figures(uidata: list[dto.UIDataDict]) -> Figure:
    df: pd.DataFrame = pd.DataFrame({
        'symbol': [ui["symbol"] for ui in uidata],
        "invested_sum": [ui["invested_sum"] for ui in uidata],
        "market_value": [ui["market_value"] for ui in uidata],
        "roi": [ui["roi"] for ui in uidata],
    })

    df['Profitability'] = np.where(df["roi"]<0, 'Loss', 'Profit')
    df = df.sort_values(by=['roi'], ascending=False)
    roifig = px.bar(df, x="symbol", y="roi", color=df['Profitability'], title="Portfolio by Return on Investment")
    roifig.update_traces(hovertemplate=
                         '<b>%{x}</b>'+
                         '<br><b>roi</b>: %{y:.2f}%<br>'
    )
    roifig.update_layout(hovermode="x")
    return roifig