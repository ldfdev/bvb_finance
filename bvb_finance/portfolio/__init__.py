import typing
import numbers
import datetime
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
from bvb_finance.portfolio import variations
from bvb_finance.portfolio.acquistions_processor import AcquisitionsProcessor
from bvb_finance.rest_api import portfolio as rest_api_portfolio 

logger = logging.getLogger()

tickers = portfolio_loader.load_portfolio_tickers()

acquisitions: list[dto.Acquisition] = loaders.load_acquisitions_data(loaders.portfolio_acquisition_details)

NullableFLoat: typing.TypeVar = float | str

@na_type.na_type_check
def compute_roi(initial_sum: NullableFLoat, final_sum: NullableFLoat) -> NullableFLoat:
    return (final_sum / initial_sum - 1) * 100

def obtain_portfolio_data(end_date: datetime.date) -> list[dto.UIDataDict]:
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

    logger.info(f"Loading market data up to {end_date}")
    market_data: dto.MarketData = loaders.load_historical_data_many_tickers(tickers)
    for grouped_acquisition in grouped_acquisitions:
        ticker: str = grouped_acquisition["symbol"]
        invested_sum: float = grouped_acquisition["invested_sum"]
        market_value, market_value_date = na_type.NAType, na_type.NAType
        data = market_data.get_market_value(ticker, date=end_date)
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
    def build_profitability(item: typing.Union[str, numbers.Number]) -> str:
        """Indicates whether item represents a 
         - Loss
         - Profit
         - n/a
        """
        if item == na_type.NAType:
            return na_type.NAType
        if item < 0:
            return 'Loss'
        return 'Profit'
    
    df['Profitability'] = pd.Series(
        [build_profitability(item)for item in df["roi"]]
    )

    # sort by roi but handle n/a values
    rows_roi_is_na = df[df['roi'] == na_type.NAType]
    # Remaining rows
    remaining_rows = df[~df.index.isin(rows_roi_is_na.index)]
    remaining_rows.sort_values(by=['roi'], ascending=False)

    # Concatenate the DataFrames
    sorted_df = pd.concat([remaining_rows, rows_roi_is_na], ignore_index=True)
    roifig = px.bar(sorted_df, x="symbol", y="roi", color=df['Profitability'], title="Portfolio by Return on Investment")
    roifig.update_traces(hovertemplate=
                         '<b>%{x}</b>'+
                         '<br><b>roi</b>: %{y:.2f}%<br>'
    )
    roifig.update_layout(hovermode="x")
    return roifig

def build_variations() -> typing.Iterable[typing.Tuple[Figure, pd.DataFrame]]:
    
    variations_of_interest: list[variations.VariationEnumMeta] = [
        variations.VariationEnum.DAILY_VAR(1),
        variations.VariationEnum.DAILY_VAR(7),
        variations.VariationEnum.MONTHLY_VAR(1),
        variations.VariationEnum.MONTHLY_VAR(3),
        variations.VariationEnum.YTD()
    ]
    for variationEnum in variations_of_interest:
        variation_df: pd.DataFrame = variations.build_tickers_variations_data(variationEnum)
        variation_df = variation_df.sort_values(by=[variationEnum.header], ascending=False)

        varfig = px.bar(variation_df, x="symbol", y=variationEnum.header,  title=f"Tickers Variation {variationEnum.header}")
        varfig.update_traces(
            customdata=np.array(variation_df[variationEnum.ref_interval]),
            hovertemplate=
                            '<b>%{x}</b>'+
                            '<br><b>var</b>: %{y:.2f}%<br>'+
                            '<br><b>' + variationEnum.ref_interval + '</b>: %{customdata:.2f}%<br>'
        )
        varfig.update_layout(hovermode="x")

        yield varfig, variation_df
