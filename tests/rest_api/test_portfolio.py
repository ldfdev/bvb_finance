import unittest
import json
import datetime
import logging
from bvb_finance.common import dto as common_dto
from bvb_finance.portfolio import dto as portfolio_dto

logger = logging.getLogger()

class TestPortfolio(unittest.TestCase):
    def test_serialization(self):
        acquisition = {
            "date": datetime.date(year=2024, month=8, day=20),
            "symbol": "AAPL",
            "quantity": 10,
            "price": 100.09,
            "fees": 0.002
        }
        acquisitions: list[portfolio_dto.Acquisition] = [
            portfolio_dto.Acquisition(acquisition)
        ]
        common_dto.SerializationObject.serialize(acquisitions)