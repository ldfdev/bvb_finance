import datetime
import enum
import itertools
import typing
import pandas as pd
from collections import defaultdict
from bvb_finance.portfolio import dto
from bvb_finance import logging

logger = logging.getLogger()

class SourceEnum(enum.Enum):
    AQUISITION = enum.auto()
    STOCK_SPLIT = enum.auto()

class TimestampHint(typing.TypedDict):
    date: datetime.date
    source: SourceEnum

class AcquisitionsProcessor:
    """
    Is able to track price movements for stocks given a list of acquisitions
    It adjusts for stock splits
    """
    acquisitions: dict[datetime.date, list[dto.Acquisition]] = dict()
    stock_splits: dict[datetime.date, list[dto.StockSplit]] = dict()
    
    def __init__(self, acquisitions: list[dto.Acquisition], stock_splits: list[dto.StockSplit]):
        AcquisitionsProcessor.acquisitions = AcquisitionsProcessor._construct_dict(acquisitions)
        AcquisitionsProcessor.stock_splits = AcquisitionsProcessor._construct_dict(stock_splits)

    @classmethod
    def process_acquisitions_from_dataframe(cls, df: pd.DataFrame) -> list[dto.Acquisition]:
        df['Pret'] = df['Pret'].apply(dto.Acquisition.convert_price_to_float)
        df['Data'] = df['Data'].apply(dto.Acquisition.convert_date_from_str)

        # columns are Data	Simbol	Cantitate	Pret	Comision
        file_columns = 'Data	Simbol	Cantitate	Pret	Comision'.split('\t')
        new_coluns = [key for key in typing.get_type_hints(dto.AcquisitionDict)]
        column_replacement = {
            old: new for old, new in zip(file_columns, new_coluns)
        }
        df.rename(columns=column_replacement, inplace=True)
        logger.info(f"Acquisitions DataFrame: {df}")
        acquisitions: list[dto.Acquisition] = [dto.Acquisition(cls._copy_dict(record)) for record in df.to_dict('records')]
        cls.acquisitions = AcquisitionsProcessor._construct_dict(acquisitions)
        return acquisitions

    @classmethod
    def process_stock_splits_from_dataframe(cls, df: pd.DataFrame) -> list[dto.StockSplit]:
        df['Data'] = df['Data'].apply(dto.StockSplit.convert_date_from_str)
        # columns are Data	Simbol	Cantitate	Split Ratio
        file_columns = 'Data	Simbol	Split Ratio'.split('\t')
        new_coluns = [key for key in typing.get_type_hints(dto.StockSplitDict)]
        column_replacement = {
            old: new for old, new in zip(file_columns, new_coluns)
        }
        df.rename(columns=column_replacement, inplace=True)
        logger.info(f"Stock Splits DataFrame: {df}")
        stock_splits: list[dto.StockSplit] = [dto.StockSplit(cls._copy_dict(record)) for record in df.to_dict('records')]
        cls.stock_splits = AcquisitionsProcessor._construct_dict(stock_splits)
        return stock_splits

    @staticmethod
    def _construct_dict(list_data: list[dto.Acquisition | dto.StockSplit]) -> dict[datetime.date, list[dto.Acquisition | dto.StockSplit]]:
        d = defaultdict(list)
        for item in list_data:
            d[item.date].append(item)
        return d
        
    @classmethod
    def group_acquisitions_data(cls) -> list[dto.UIPartialDataCostOfAcquisition]:
        visited: typing.Dict[str, dto.UIPartialDataCostOfAcquisition] = dict()
        for timestampHint in cls._aggregate_timestamps():
            date = timestampHint["date"]
            source = timestampHint["source"]
            if source == SourceEnum.AQUISITION:
                [cls._aggregate_acquisition(visited, acquisition) for acquisition in cls.acquisitions.get(date)]
            elif source == SourceEnum.STOCK_SPLIT:
                [cls._adjust_price_for_stock_split(visited, stock_split) for stock_split in cls.stock_splits.get(date)]

        result = [v for v in visited.values()]
        result.sort(key = lambda d: d["symbol"])
        logger.info(f"Constructed grouped acquisitions data: {result}")
        return result
    
    @classmethod
    def _aggregate_acquisition(cls, visited: typing.Dict[str, dto.UIPartialDataCostOfAcquisition], acquisition: dto.Acquisition):
        cache: typing.Optional[dto.UIPartialDataCostOfAcquisition] = visited.get(acquisition.symbol) 
        if cache is None:
            cache = {
                "date": acquisition.date,
                "symbol": acquisition.symbol,
                "invested_sum": 0.0,
                "num_of_shares": 0,
                "fees": 0.0
            }
            visited[acquisition.symbol] = cache

        # logger.info("_aggregate_acquisition: updating cache")
        # logger.info(f"cache {type(cache)} = {cache}")
        # logger.info(f"Acquisition {type(acquisition)} = {acquisition}")
        
        cache["num_of_shares"] += acquisition.quantity
        cache["invested_sum"] += acquisition.price
        cache["fees"] += acquisition.fees
        cache["date"] = acquisition.date
        logger.info(f"Aggregated acquisition based on {acquisition}. Result = {cache}")
    
    @classmethod
    def _adjust_price_for_stock_split(cls, visited: typing.Dict[str, dto.Acquisition], stock_split: dto.StockSplit):
        partialDataCostOfAcquisition: typing.Optional[dto.UIPartialDataCostOfAcquisition] = visited.get(stock_split.symbol)
        if partialDataCostOfAcquisition is None:
            logger.info(f"Adjusting price for stock split {stock_split.dict}. No acquisition of stock {stock_split.symbol} found")
            return
        new = cls._copy_dict(partialDataCostOfAcquisition)
        new["num_of_shares"] = stock_split.get_new_shares_quantity(partialDataCostOfAcquisition["num_of_shares"])

        logger.info(f"Adjusting price for stock split {stock_split.dict}. Old {partialDataCostOfAcquisition} New {new}")
        visited[stock_split.symbol] = new

    @classmethod
    def _aggregate_timestamps(cls) -> list[TimestampHint]:
        '''
        merges acquisitions and stock_splits by date.
        Prioritizes acquisitions over stock_splits whetn dates are equal
        '''
        acquisition_timestamps: list[TimestampHint] = [
            {"date": date, "source": SourceEnum.AQUISITION} for date in cls.acquisitions
        ]
        logger.info(f"_aggregate_timestamps: acquisition_timestamps={acquisition_timestamps}")
        
        stock_split_timestamps: list[TimestampHint] = [
            {"date": date, "source": SourceEnum.STOCK_SPLIT} for date in cls.stock_splits
        ]
        logger.info(f"_aggregate_timestamps: stock_split_timestamps={stock_split_timestamps}")

        timestamps: list[TimestampHint] = list()
        acquisition_iter = cls._get_infinite_iter(acquisition_timestamps)
        stock_split_iter = cls._get_infinite_iter(stock_split_timestamps)

        acquisition_timestamp = next(acquisition_iter)
        stock_split_timestamp = next(stock_split_iter)
        while True:
            # logger.info(f"_aggregate_timestamps(acquisition_timestamp={acquisition_timestamp}, stock_split_timestamp={stock_split_timestamp})")
            if not any((acquisition_timestamp, stock_split_timestamp)):
                break
            if acquisition_timestamp is None:
                timestamps.append(stock_split_timestamp)
                stock_split_timestamp = next(stock_split_iter)
            elif stock_split_timestamp is None:
                timestamps.append(acquisition_timestamp)
                acquisition_timestamp = next(acquisition_iter)
            elif acquisition_timestamp["date"] <= stock_split_timestamp["date"]:
                timestamps.append(acquisition_timestamp)
                acquisition_timestamp = next(acquisition_iter)
            else:
                timestamps.append(stock_split_timestamp)
                stock_split_timestamp = next(stock_split_iter)

        logger.info(f"_aggregate_timestamps: all timestamps: {timestamps}")
        return timestamps
    
    @classmethod
    def _get_infinite_iter(cls, source):
        return itertools.chain(source, itertools.cycle([None]))
    
    @classmethod
    def _copy_dict(cls, d: typing.Dict) -> typing.Dict:
        return {key: d[key] for key in d}
