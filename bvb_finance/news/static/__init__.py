import typing
from bvb_finance.common import dto as common_dto

class StaticNewsDict(typing.TypedDict):
    url: str
    description: str

class StaticNews(common_dto.DictConverter):
    pass

def static_news(news_list: list[StaticNewsDict]) -> list[StaticNews]:
    return [StaticNews(dict_) for dict_ in news_list]

romania_news = static_news([
    {
        "url": "https://cursdeguvernare.ro/",
        "description": "cursdeguvernare.ro"
    },
    {
        "url": "https://financialmarket.ro/",
        "description": "financialmarket.ro"
    },
    {
        "url": "https://www.profit.ro/",
        "description": "profit.ro"
    },
    {
        "url": "https://www.bursa.ro/",
        "description": "bursa.ro"
    },
    {
        "url": "https://www.piatafinanciara.ro/",
        "description": "piatafinanciara.ro"
    },
    {
        "url": "https://www.finzoom.ro/",
        "description": "finzoom.ro"
    },
    {
        "url": "https://www.financialintelligence.ro/",
        "description": "financialintelligence.ro"
    }
])