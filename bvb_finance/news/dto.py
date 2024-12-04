import datetime
import typing
from bvb_finance.common import dto as common_dto

class NewsDict(typing.TypedDict):
    date: datetime.date
    source: str
    tite: str
    content: str
