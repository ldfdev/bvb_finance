import unittest
from bvb_finance.company_reports import dto
import datetime

class TestWebsite_Company(unittest.TestCase):
    def test(self):
        company = dto.Website_Company()
        company.name = 'Company LLT'
        company.ticker = 'ABC'
        company.documents = [
            dto.Website_Financial_Document(
                "my description",
                "file:..non-existent-ulr",
                datetime.date(2024, 10, 1),
                datetime.time(14, 25, 0)
            )
        ]

        serialized = company.serialize()
        print('Serialized form', serialized)
