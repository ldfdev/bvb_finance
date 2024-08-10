import typing
import json
import pandas as pd
from bvb_finance.common import dto as common_dto

class Evolutie(typing.TypedDict):
    time: int
    value: int

class CompanyMarketCapDict(typing.TypedDict):
    simbol: str
    nume: str
    pret: float
    capitalizare: int
    divy: float
    anDividenend: str
    divyAnual: str
    anDivY: int
    volum1y: str
    var1y: str
    var7d: float
    var1sapt: float
    evolutie: typing.List[Evolutie]


class CompanyMarketCap(common_dto.DictConverter):
    @staticmethod
    def from_str(s: str) -> 'CompanyMarketCap':
        dict_ = json.loads(s)
        return CompanyMarketCap(dict_)

class MarketCapDataUiPayloadDict(typing.TypedDict):
    modofication_date: str
    data: pd.DataFrame

class MarketCapDataUiPayload(common_dto.DictConverter):
    pass