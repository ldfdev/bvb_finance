import unittest
import typing
import datetime

from bvb_finance import layouts
from bvb_finance.company_reports import dto

class TestLayouts(unittest.TestCase):
    def test_filter_reports_based_on_date(self):
        old_reports: list[dto.Website_Company] = [
            dto.Website_Company(
                name='Company 1',
                ticker='Company 1',
                documents=[
                    dto.Website_Financial_Document(
                        description='old document (1) for Company 1',
                        url='path/to/document1',
                        modification_date=datetime.datetime(year=2022, month=10, day=20).date()
                    ),
                    dto.Website_Financial_Document(
                        description='old document (2) for Company 1',
                        url='path/to/document2',
                        modification_date=datetime.datetime(year=2023, month=4, day=20).date()
                    )
            ]),
            dto.Website_Company(
                name='Company AQ',
                ticker='Company AQ',
                documents=[
                    dto.Website_Financial_Document(
                        description='old document (1) for Company AQ',
                        url='path/to/document1AQ',
                        modification_date=datetime.datetime(year=2022, month=12, day=11).date()
                    ),
                    dto.Website_Financial_Document(
                        description='old document (2) for Company AQ',
                        url='path/to/document2AQ',
                        modification_date=datetime.datetime(year=2023, month=9, day=21).date()
                    )
            ])
        ]

        valid_documents = [
            dto.Website_Financial_Document(
                description='old document (1) for Company 2',
                url='path/to/document1',
                modification_date=datetime.datetime(year=2024, month=10, day=20).date()
            ),
            dto.Website_Financial_Document(
                description='old document (21) for Company 2',
                url='path/to/document11',
                modification_date=datetime.datetime(year=2024, month=10, day=30).date()
            ),
            dto.Website_Financial_Document(
                description='old document (1012) for Company 2',
                url='path/to/document1012',
                modification_date=datetime.datetime(year=2024, month=10, day=2).date()
            ),
            dto.Website_Financial_Document(
                description='old document (1) for Company 3',
                url='path/to/document1',
                modification_date=datetime.datetime(year=2024, month=10, day=1).date()
            ),
            dto.Website_Financial_Document(
                description='old document (2) for Company 3',
                url='path/to/document2',
                modification_date=datetime.datetime(year=2024, month=10, day=15).date()
            ),

        ]

        company_3: dto.Website_Company = dto.Website_Company(
            name='Company 3',
            ticker='Company 3',
            documents=[
                valid_documents[2],
                valid_documents[3],
        ])

        valid_reports: list[dto.Website_Company] = [
            dto.Website_Company(
                name='Company 2',
                ticker='Company 2',
                documents=[
                    dto.Website_Financial_Document(
                        description='old document (1) for Company 2',
                        url='path/to/document1',
                        modification_date=datetime.datetime(year=2024, month=8, day=20).date()
                    ),
                    dto.Website_Financial_Document(
                        description='old document (2) for Company 1',
                        url='path/to/document2',
                        modification_date=datetime.datetime(year=2023, month=8, day=20).date()
                    ),
                    valid_documents[0],
                    valid_documents[1],
            ]),
            company_3
        ]

        all_reports: list[dto.Website_Compan] = old_reports + valid_reports

        start_date=datetime.datetime(year=2024, month=10, day=1)
        end_date=None
        filtered: list[dto.Website_Compan] = layouts.filter_reports_based_on_date(all_reports, start_date, end_date)

        self.assertEqual(len(filtered), 2)
        for old in old_reports:
            self.assertTrue(old not in filtered)

        company_2: typing.Optional[dto.Website_Company] = None
        company_2_name = 'Company 2'
        company_2_ticker = 'Company 2'
        for report in filtered:
            if report.name == company_2_name:
                company_2 = report
                break
        self.assertTrue(company_2 is not None)
        self.assertEqual(company_2.ticker, company_2_ticker)
        self.assertEqual(len(company_2.documents), 2)
        self.assertTrue(valid_documents[0] in company_2.documents)
        self.assertTrue(valid_documents[1] in company_2.documents)

        self.assertTrue(company_3 in filtered)
        

