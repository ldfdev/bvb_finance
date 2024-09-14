import unittest
import datetime
import pandas as pd
from bvb_finance.portfolio import loaders
from bvb_finance.portfolio import dto
from bvb_finance import portfolio
from bvb_finance.portfolio.acquistions_processor import AcquisitionsProcessor
from .. import get_full_path

class TestPortfolio(unittest.TestCase):
    def test_acquistion_types(self):
        d = {
            "date": "05.01.2024",
            "symbol": "TEL",
            "quantity": 10,
            "price": 10100.2,
            "fees": 111.04
        }
        a: dto.Acquisition = dto.Acquisition(d)
        self.assertTrue(isinstance(a.date, datetime.date), f"Expected 'date' to be a instance of datetime.date in {str(a)}")
        self.assertTrue(isinstance(a.price, float), f"Expected 'price' to be a instance of float in {str(a)}")


    def test_load_portfolio(self):
        portfolio_acquisition_details = get_full_path("portfolio_acquisition_details.tsv")
        acquisitions_df: pd.DataFrame = loaders.load_acquisitions_data(portfolio_acquisition_details)
        acquisitions: list[dto.Acquisition] = AcquisitionsProcessor.process_acquisitions_from_dataframe(acquisitions_df)
        self.assertEqual(len(acquisitions), 7, [str(a) for a in acquisitions])
        first = """{
    "date": "05.01.2024",
    "symbol": "TEL",
    "quantity": 10,
    "price": 10100.2,
    "fees": 111.04
}"""
        self.assertEqual(str(acquisitions[0]), first)

        last = """{
    "date": "26.01.2024",
    "symbol": "H2O",
    "quantity": 300,
    "price": 36570.0,
    "fees": 555.5555
}"""
        self.assertEqual(str(acquisitions[-1]), last)

    def convert_params(self, d: dto.AcquisitionDict) -> dto.AcquisitionDict:
        d['price'] = dto.Acquisition.convert_price_to_float(d['price'])
        d['date'] = dto.Acquisition.convert_date_from_str(d['date'])
        return d
        
    def test_portfolio_construction_should_sort(self):
        acquisitions_inorder = [
            {
                "date": "26.01.2024",
                "symbol": "A20",
                "quantity": 300,
                "price": 100,
                "fees": 1
            },
            {
                "date": "26.01.2024",
                "symbol": "H2O",
                "quantity": 200,
                "price": 100,
                "fees": 1
            },
            {
                "date": "26.01.2024",
                "symbol": "H2O",
                "quantity": 100,
                "price": 100,
                "fees": 1
            },
            {
                "date": "20.01.2024",
                "symbol": "ABC",
                "quantity": 300,
                "price": 100,
                "fees": 1
            },
            {
                "date": "23.01.2024",
                "symbol": "H3O",
                "quantity": 300,
                "price": 100,
                "fees": 1
            },
        ]
        acquisitions_inorder = [dto.Acquisition(a) for a in acquisitions_inorder]

        p = dto.Portfolio(acquisitions_inorder)

        acquisitions_ordered = [
            {
                "date": datetime.date(year=2024, month=1,day=20),
                "symbol": "ABC",
                "quantity": 300,
                "price": 100.0,
                "fees": 1
            },
            {
                "date": datetime.date(year=2024, month=1,day=23),
                "symbol": "H3O",
                "quantity": 300,
                "price": 100.0,
                "fees": 1
            },
            {
                "date": datetime.date(year=2024, month=1,day=26),
                "symbol": "A20",
                "quantity": 300,
                "price": 100.0,
                "fees": 1
            },
            {
                "date": datetime.date(year=2024, month=1,day=26),
                "symbol": "H2O",
                "quantity": 100,
                "price": 100.0,
                "fees": 1
            },
            {
                "date": datetime.date(year=2024, month=1,day=26),
                "symbol": "H2O",
                "quantity": 200,
                "price": 100.0,
                "fees": 1
            }
        ]

        for expected, actual in zip(acquisitions_ordered,
                                    [a.dict for a in p.acquisitions]):
            self.assertEqual(expected, actual)

    def test_portfolio_construction_should_skip_sort(self):
        acquisitions_inorder = [
            {
                "date": "26.01.2024",
                "symbol": "H2O",
                "quantity": 100,
                "price": 100,
                "fees": 1
            },
            {
                "date": "20.01.2024",
                "symbol": "ABC",
                "quantity": 300,
                "price": 100,
                "fees": 1
            },
            {
                "date": "23.01.2024",
                "symbol": "H3O",
                "quantity": 300,
                "price": 100,
                "fees": 1
            },
        ]

        expected = [
            {
                "date": datetime.date(year=2024, month=1,day=26),
                "symbol": "H2O",
                "quantity": 100,
                "price": 100.0,
                "fees": 1
            },
            {
                "date": datetime.date(year=2024, month=1,day=20),
                "symbol": "ABC",
                "quantity": 300,
                "price": 100.0,
                "fees": 1
            },
            {
                "date": datetime.date(year=2024, month=1,day=23),
                "symbol": "H3O",
                "quantity": 300,
                "price": 100.0,
                "fees": 1
            },
        ]
        acquisitions = [dto.Acquisition(a) for a in acquisitions_inorder]

        p = dto.Portfolio.construct_from_sorted(acquisitions)

        for expected, actual in zip(expected,
                                    [a.dict for a in p.acquisitions]):
            self.assertEqual(expected, actual)
    
    def test_get_at_date(self):
        acquisitions_inorder = [
            {
                "date": "26.01.2024",
                "symbol": "H2O",
                "quantity": 100,
                "price": 100,
                "fees": 1
            },
            {
                "date": "20.01.2024",
                "symbol": "ABC",
                "quantity": 300,
                "price": 100,
                "fees": 1
            },
            {
                "date": "23.01.2024",
                "symbol": "H3O",
                "quantity": 300,
                "price": 100,
                "fees": 1
            },
        ]
        acquisitions = [dto.Acquisition(a) for a in acquisitions_inorder]

        p = dto.Portfolio(acquisitions)

        p2 = p.get_at_date(datetime.date(year=2023, month=10, day=25))
        self.assertEqual(len(p2.acquisitions), 0, f"Expected portfolio with 0 elements; but got {p2.acquisitions}")
        
        p2 = p.get_at_date(datetime.date(year=2024, month=1, day=22))
        self.assertEqual(len(p2.acquisitions), 1, f"Expected portfolio with 1 elements; but got {p2.acquisitions}")
        p2_acquisition: dto.Acquisition = p2.acquisitions[0]
        self.assertEqual({
            "date": datetime.date(year=2024, month=1,day=20),
            "symbol": "ABC",
            "quantity": 300,
            "price": 100.0,
            "fees": 1
        }, p2_acquisition.dict)
        
        p2 = p.get_at_date(datetime.date(year=2024, month=1, day=23))
        self.assertEqual(len(p2.acquisitions), 2, f"Expected portfolio with 2 elements; but got {p2.acquisitions}")
    
    def test_get_acquisition_price(self):
        acquisitions = [
            {
                "date": "26.01.2024",
                "symbol": "H2O",
                "quantity": 10,
                "price": 10,
                "fees": 1
            },
            {
                "date": "20.01.2024",
                "symbol": "ABC",
                "quantity": 30,
                "price": 10,
                "fees": 1
            },
            {
                "date": "23.01.2024",
                "symbol": "H3O",
                "quantity": 4400,
                "price": 1,
                "fees": 1
            },
        ]
        acquisitions = [dto.Acquisition(a) for a in acquisitions]

        p = dto.Portfolio(acquisitions)

        self.assertEqual(100 + 300 + 4400, p.get_acquisition_price())
        self.assertEqual(100 + 300 + 4400 + 3, p.get_acquisition_price(include_fees=True))
        
    def test_historical_data_convert_symbol_from_trading_view_format(self):
        value: str = dto.HistoricalData.convert_symbol_from_trading_view_format("BVB:SNP")
        self.assertEqual(value, "SNP")

    def test_historical_data_convert_date_from_str(self):
        date: datetime.date = dto.HistoricalData.convert_date_from_str("2024-06-17 10:00:00")
        self.assertEqual(date.year, 2024)
        self.assertEqual(date.month, 6)
        self.assertEqual(date.day, 17)
    
    def test_historical_data_load_historical_data_single_ticker(self):
        historical_data_file = get_full_path("historical_data_single_ticker.csv")
        df: pd.DataFrame = loaders.load_historical_data_single_ticker(historical_data_file)
        expected_columns = "date,symbol,open,high,low,close,volume".split(",")
        self.assertEqual(list(df.columns), expected_columns)
        self.assertEqual("SNP", next(iter(set(df['symbol']))))
        self.assertEqual(list(df.index), list(range(len(df))), f"Test that load_historical_data_single_ticker uses numeric indexing failed")
    
    def test_market_data(self):
        files = [
            get_full_path("historical_data_A1.csv"),
            get_full_path("historical_data_A2.csv"),
            get_full_path("historical_data_A3.csv")
        ]

        market_data: dto.MarketData = loaders.load_historical_data_many_tickers(files)
        dates: list[datetime.date] = market_data.get_dates()
        self.assertEqual(sorted(dates), dates, f"Expected market data to be sorted by date")
        
        closest: datetime.date = market_data.find_closest_date(datetime.date(year=2014, month=12, day=20))
        self.assertEqual(closest, None)

        closest: datetime.date = market_data.find_closest_date(datetime.date(year=2014, month=12, day=27))
        self.assertEqual(closest.year, 2014)
        self.assertEqual(closest.month, 12)
        self.assertEqual(closest.day, 22)

        closest: datetime.date = market_data.find_closest_date(datetime.date(year=2014, month=12, day=29))
        self.assertEqual(closest.year, 2014)
        self.assertEqual(closest.month, 12)
        self.assertEqual(closest.day, 29)

        # latest date is 2015-01-12
        closest: datetime.date = market_data.get_newest_date()
        self.assertEqual(closest.year, 2015)
        self.assertEqual(closest.month, 1)
        self.assertEqual(closest.day, 12)

        (value,_) = market_data.get_market_value("A1")
        self.assertEqual(value, 20250112)

        closest: datetime.date = market_data.find_closest_date(datetime.date(year=2014, month=12, day=20),
                                                               criterion=dto.MarketData.DateComparison.NOT_LT)
        self.assertEqual(closest.year, 2014)
        self.assertEqual(closest.month, 12)
        self.assertEqual(closest.day, 22)

        closest: datetime.date = market_data.find_closest_date(datetime.date(year=2014, month=12, day=27),
                                                               criterion=dto.MarketData.DateComparison.NOT_LT)
        self.assertEqual(closest.year, 2014)
        self.assertEqual(closest.month, 12)
        self.assertEqual(closest.day, 29)

        closest: datetime.date = market_data.find_closest_date(datetime.date(year=2014, month=12, day=29),
                                                               criterion=dto.MarketData.DateComparison.NOT_LT)
        self.assertEqual(closest.year, 2015)
        self.assertEqual(closest.month, 1)
        self.assertEqual(closest.day, 5)

        closest: datetime.date = market_data.find_closest_date(datetime.date(year=2015, month=12, day=29),
                                                               criterion=dto.MarketData.DateComparison.NOT_LT)
        self.assertEqual(closest, None)

    def test_group_acquisitions_data_no_stock_splits_same_date(self):
        acquisitions: list[dto.Acquisition] = [
            {
                "symbol": "A",
                "quantity": 1,
                "price": 100,
                "fees": 1,
                "date": "1.1.2000"
            },
            {
                "symbol": "B",
                "quantity": 1,
                "price": 2000,
                "fees": 1,
                "date": "1.1.2000"
            },
            {
                "symbol": "A",
                "quantity": 1,
                "price": 200,
                "fees": 1,
                "date": "1.1.2000"
            },
            {
                "symbol": "A",
                "quantity": 3,
                "price": 100,
                "fees": 1,
                "date": "1.1.2000"
            },
        ]
        acquisitions = [dto.Acquisition(a) for a in acquisitions]
        stock_splits = list()

        ap: AcquisitionsProcessor = AcquisitionsProcessor(acquisitions, stock_splits)
        
        resulted_list: list[dto.Acquisition] = AcquisitionsProcessor.group_acquisitions_data()
        self.assertEqual(len(resulted_list), 2)

        first: dto.UIPartialDataCostOfAcquisition = resulted_list[0]
        self.assertEqual(first["symbol"], "A")
        self.assertEqual(first["invested_sum"], float(100 + 200 + 100))
        self.assertEqual(first["num_of_shares"], 1 + 1 + 3)
        self.assertEqual(first["fees"], float(1 + 1 + 1))
        self.assertEqual(first["date"], datetime.date(year=2000, month=1, day=1))

        second: dto.UIPartialDataCostOfAcquisition = resulted_list[1]
        self.assertEqual(second["symbol"], "B")
        self.assertEqual(second["invested_sum"], float(2000))
        self.assertEqual(second["num_of_shares"], 1)
        self.assertEqual(second["fees"], float(1))
        self.assertEqual(second["date"], datetime.date(year=2000, month=1, day=1))
    
    def test_group_acquisitions_data_no_stock_splits_different_dates(self):
        acquisitions: list[dto.Acquisition] = [
            {
                "symbol": "A",
                "quantity": 1,
                "price": 100,
                "fees": 1,
                "date": "1.1.2001"
            },
            {
                "symbol": "B",
                "quantity": 1,
                "price": 2000,
                "fees": 1,
                "date": "1.1.2000"
            },
            {
                "symbol": "A",
                "quantity": 1,
                "price": 200,
                "fees": 1,
                "date": "1.1.2002"
            },
            {
                "symbol": "A",
                "quantity": 3,
                "price": 100,
                "fees": 1,
                "date": "1.1.2010"
            },
        ]
        acquisitions = [dto.Acquisition(a) for a in acquisitions]
        stock_splits = list()

        ap: AcquisitionsProcessor = AcquisitionsProcessor(acquisitions, stock_splits)
        
        resulted_list: list[dto.Acquisition] = AcquisitionsProcessor.group_acquisitions_data()
        self.assertEqual(len(resulted_list), 2)

        first: dto.UIPartialDataCostOfAcquisition = resulted_list[0]
        self.assertEqual(first["symbol"], "A")
        self.assertEqual(first["invested_sum"], float(100 + 200 + 100))
        self.assertEqual(first["num_of_shares"], 1 + 1 + 3)
        self.assertEqual(first["fees"], float(1 + 1 + 1))
        self.assertEqual(first["date"], datetime.date(year=2010, month=1, day=1))

        second: dto.UIPartialDataCostOfAcquisition = resulted_list[1]
        self.assertEqual(second["symbol"], "B")
        self.assertEqual(second["invested_sum"], float(2000))
        self.assertEqual(second["num_of_shares"], 1)
        self.assertEqual(second["fees"], float(1))
        self.assertEqual(second["date"], datetime.date(year=2000, month=1, day=1))
    
    def test_group_acquisitions_data_no_stock_using_stock_splits(self):
        acquisitions: list[dto.Acquisition] = [
            {
                "symbol": "A",
                "quantity": 1,
                "price": 100,
                "fees": 1,
                "date": "1.1.2001"
            },
            {
                "symbol": "B",
                "quantity": 1,
                "price": 2000,
                "fees": 1,
                "date": "1.1.2000"
            },
            {
                "symbol": "A",
                "quantity": 1,
                "price": 200,
                "fees": 1,
                "date": "1.1.2002"
            },
            {
                "symbol": "A",
                "quantity": 3,
                "price": 100,
                "fees": 1,
                "date": "1.1.2010"
            },
        ]
        acquisitions = [dto.Acquisition(a) for a in acquisitions]

        stock_splits: list[dto.StockSplit]  = [
            {
                "date": "20.08.2008",
                "symbol": "XYZ",
                "split_ratio": "1/1",
            },
            {
                "date": "28.08.1996",
                "symbol": "B",
                "split_ratio": "1/1",
            },
            {
                "date": "20.08.2008",
                "symbol": "A",
                "split_ratio": "100/1",
            },
        ]
        stock_splits = [dto.StockSplit(a) for a in stock_splits]

        ap: AcquisitionsProcessor = AcquisitionsProcessor(acquisitions, stock_splits)
        
        resulted_list: list[dto.Acquisition] = AcquisitionsProcessor.group_acquisitions_data()
        self.assertEqual(len(resulted_list), 2)

        first: dto.UIPartialDataCostOfAcquisition = resulted_list[0]
        self.assertEqual(first["symbol"], "A")
        self.assertEqual(first["invested_sum"], float(100 + 200 + 100))
        self.assertEqual(first["num_of_shares"], 100 + 100 + 3)
        self.assertEqual(first["fees"], float(1 + 1 + 1))
        self.assertEqual(first["date"], datetime.date(year=2010, month=1, day=1))

        second: dto.UIPartialDataCostOfAcquisition = resulted_list[1]
        self.assertEqual(second["symbol"], "B")
        self.assertEqual(second["invested_sum"], float(2000))
        self.assertEqual(second["num_of_shares"], 1)
        self.assertEqual(second["fees"], float(1))
        self.assertEqual(second["date"], datetime.date(year=2000, month=1, day=1))