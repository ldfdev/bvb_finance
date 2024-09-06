import pandas as pd
import numpy as np
import datetime
import unittest
from bvb_finance.portfolio import dto
from bvb_finance.portfolio import variations

class TestVariations(unittest.TestCase):
    def test_build_portfolio_variations_data(self):
        input: pd.DataFrame = pd.DataFrame([
            {
                "date": datetime.date(year=2024, month=4, day=10),
                "symbol": "A1",
                "open": 10,
                "high": 20,
                "low": 8,
                "close": 9,
                "volume": 100
            },
            {
                "date": datetime.date(year=2024, month=4, day=20),
                "symbol": "A1",
                "open": 10,
                "high": 18,
                "low": 8,
                "close": 9,
                "volume": 100
            },
        ])
        dto.MarketData.df = input
        df: pd.DataFrame = variations.build_portfolio_variations_data()
        df_columns: list[str] = list(df.columns)
        self.assertFalse("1 Day Var" in df_columns)

        new_row = {
                "date": datetime.date(year=2024, month=4, day=19),
                "symbol": "A1",
                "open": 10,
                "high": 20,
                "low": 8,
                "close": 9,
                "volume": 100
            }
        input = input._append(new_row, ignore_index = True)
        df: pd.DataFrame = variations.build_portfolio_variations_data()
        df_columns: list[str] = list(df.columns)
        # self.assertTrue("1 Day Var" in df_columns)

    def test_timedelta_in_days(self):
        first = datetime.date(year=2024, month=8, day=20)
        middle = datetime.date(year=2024, month=1, day=20)
        last = datetime.date(year=2024, month=8, day=21)
        diff: int = variations.timedelta_in_days([first, middle, last])
        self.assertTrue(diff, 1)
    
    def test_tickers_variations_data(self):
        input: pd.DataFrame = pd.DataFrame([
             [datetime.date(year=2024, month=4, day=10), "A1", 10, 20, 8, 9, 100],
             [datetime.date(year=2024, month=4, day=11), "A1", 10, 20, 8, 18, 100],

             [datetime.date(year=2024, month=4, day=10), "B1", 10, 20, 8, 13, 100],
             [datetime.date(year=2024, month=4, day=11), "B1", 10, 20, 8, 10, 100],
            ],
            columns=["date", "symbol", "open", "high", "low", "close", "volume"]
        )
        dto.MarketData.df = input

        df: pd.DataFrame = variations.build_tickers_variations_data(variations.VariationEnum.VAR_1_DAY)
        columns = list(df.columns)
        self.assertEqual(columns, ["symbol", "1 Day Var"])
        self.assertEqual(len(df), 2)
        records: dict = df.to_dict(orient='records')
        self.assertEqual(records[0]["symbol"], "A1")
        self._compare_floats(records[0]["1 Day Var"], 100.0)
        
        self.assertEqual(records[1]["symbol"], "B1")
        self._compare_floats(records[1]["1 Day Var"], -23.07)
        
    def test_tickers_variations_data_no_daily_data_available(self):
        # B1 company does not provide consecutive dates to be able to compute 1 day price variation
        input: pd.DataFrame = pd.DataFrame([
             [datetime.date(year=2024, month=4, day=10), "A1", 10, 20, 8, 9, 100],
             [datetime.date(year=2024, month=4, day=11), "A1", 10, 20, 8, 18, 100],

             [datetime.date(year=2024, month=2, day=10), "B1", 10, 20, 4, 14.89, 100],
             [datetime.date(year=2024, month=4, day=11), "B1", 10, 20, 8, 10, 100],
            ],
            columns=["date", "symbol", "open", "high", "low", "close", "volume"]
        )
        dto.MarketData.df = input

        df: pd.DataFrame = variations.build_tickers_variations_data(variations.VariationEnum.VAR_1_DAY)
        columns = list(df.columns)
        self.assertEqual(columns, ["symbol", "1 Day Var"])
        self.assertEqual(len(df), 2)
        records: dict = df.to_dict(orient='records')
        self.assertEqual(records[0]["symbol"], "A1")
        self._compare_floats(records[0]["1 Day Var"], 100.0)
        
        self.assertEqual(records[1]["symbol"], "B1")
        self.assertTrue(np.isnan(records[1]["1 Day Var"]), f"""Expected <1 Day Var> to be Nan. but it is {records[1]["1 Day Var"]}""")
    
    def test_tickers_variations_data_VAR_7_DAYS(self):
        input: pd.DataFrame = pd.DataFrame([
             [datetime.date(year=2024, month=4, day=10), "A1", 10, 20, 8, 9, 100],
             [datetime.date(year=2024, month=4, day=17), "A1", 10, 20, 8, 18, 100],

             [datetime.date(year=2023, month=4, day=10), "B1", 10, 20, 4, 14.89, 100],
             [datetime.date(year=2023, month=4, day=17), "B1", 10, 20, 8, 10, 100],
            ],
            columns=["date", "symbol", "open", "high", "low", "close", "volume"]
        )
        dto.MarketData.df = input

        df: pd.DataFrame = variations.build_tickers_variations_data(variations.VariationEnum.VAR_7_DAYS)
        columns = list(df.columns)
        self.assertEqual(columns, ["symbol", "7 Day Var"])
        self.assertEqual(len(df), 2)
        records: dict = df.to_dict(orient='records')
        self.assertEqual(records[0]["symbol"], "A1")
        self._compare_floats(records[0]["7 Day Var"], 100.0)
        
        self.assertEqual(records[1]["symbol"], "B1")
        self._compare_floats(records[1]["7 Day Var"], -32.84)
    
    def _compare_floats(self, f1, f2):
        self.assertTrue(abs(f1 - f2) < 1e-2, f"Numbers are not equal: {f1} and {f2}")