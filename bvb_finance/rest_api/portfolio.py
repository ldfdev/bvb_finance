import pandas as pd
import operator
from bvb_finance.common import dto as common_dto
from bvb_finance.common import portfolio_loader
from bvb_finance.portfolio import loaders as portfolio_loaders
from bvb_finance.portfolio import dto
from bvb_finance.portfolio.acquistions_processor import AcquisitionsProcessor

def get_portfolio_tickers() -> list[str]:
    return portfolio_loader.load_portfolio_tickers()

def get_acquisitions_data() -> list[dto.Acquisition]:
    acquisitions_df: pd.DataFrame = portfolio_loaders.load_acquisitions_data(portfolio_loaders.portfolio_acquisition_details)
    acquisitions: list[dto.Acquisition] = AcquisitionsProcessor.process_acquisitions_from_dataframe(acquisitions_df)
    acquisitions.sort(key=operator.attrgetter('date', 'symbol'), reverse=True)
    return acquisitions

def get_acquisitions_data_as_json() -> str:
    acquisitions: list[dto.Acquisition] = get_acquisitions_data()
    return common_dto.SerializationObject.serialize(acquisitions)
