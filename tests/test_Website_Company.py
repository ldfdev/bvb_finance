import unittest
from bvb_finance.company_reports import dto
import datetime

class TestWebsite_Company(unittest.TestCase):
    def test_serialize(self):
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
    
    def test_deserialize(self):
        mongo_object = {
            "documents" : [
                {
                    "description" : "Raportare ESG 2023",
                    "modification_date" : "2024-06-27",
                    "modification_time" : "12:00:17",
                    "url" : "infocont/infocont24/AQ_20240627113002_Anunt-raport-sustenabilitate-2023.pdf"
                },
                {
                    "description" : "Raportare ESG 2023",
                    "modification_date" : "2024-06-27",
                    "modification_time" : "12:00:17",
                    "url" : "infocont/infocont24/AQ_20240627113002_Raport-de-Sustenabilitate-Aquila-2023.pdf"
                }
            ],
            "name" : "AQUILA PART PROD COM",
            "ticker" : "AQ"
        }
        py_object = dto.Website_Company.deserialize(mongo_object)
        self.assertEqual(py_object.name, "AQUILA PART PROD COM")
        self.assertEqual(py_object.ticker, "AQ")
        for py_obj, mongo_obj in zip(py_object.documents, mongo_object["documents"]):
            self.assertEqual(py_obj.description, mongo_obj["description"])
            self.assertEqual(py_obj.modification_date.year, 2024)
            self.assertEqual(py_obj.modification_date.month, 6)
            self.assertEqual(py_obj.modification_date.day, 27)
            self.assertEqual(py_obj.modification_time.hour, 12)
            self.assertEqual(py_obj.modification_time.minute, 0)
            self.assertEqual(py_obj.modification_time.second, 17)
            self.assertEqual(py_obj.url, mongo_obj["url"])

