import unittest
import datetime
import pandas as pd
from bvb_finance.portfolio import trading_view

class TestPortfolio(unittest.TestCase):
    def test_identical_frames(self):
        frame: pd.DataFrame = pd.DataFrame([
            [datetime.date(2010, 12, 22), 'BBB', 1, 10, 0.2, 9, 100],
            [datetime.date(2011, 12, 22), 'BBB', 1, 10, 0.2, 9, 100],
            [datetime.date(2012, 12, 22), 'BBB', 1, 10, 0.2, 9, 100]
            ],
            columns = ['date', 'symbol', 'open', 'high', 'low', 'close', 'volume'])
        
        duplicate: pd.DataFrame = frame.copy(deep=True)
        result: pd.DataFrame = trading_view.merge_dataframes(frame, duplicate)
        diff: pd.DataFrame = frame.compare(result)
        self.assertTrue(diff.empty)
    
    def _test_merge(self, frame1):
        frame2: pd.DataFrame = pd.DataFrame([
            [datetime.date(2010, 12, 22), 'BBB', 2, 20, 2.2, 2, 200],
            [datetime.date(2020, 12, 22), 'BBB', 1, 10, 0.2, 9, 100],
            [datetime.date(2021, 12, 22), 'BBB', 1, 10, 0.2, 9, 100]
            ],
            columns = ['date', 'symbol', 'open', 'high', 'low', 'close', 'volume'])
        expected: pd.DataFrame = pd.DataFrame([
            [datetime.date(2010, 12, 22), 'BBB', 1, 10, 0.2, 9, 100],
            [datetime.date(2011, 12, 22), 'BBB', 1, 10, 0.2, 9, 100],
            [datetime.date(2012, 12, 22), 'BBB', 1, 10, 0.2, 9, 100],
            [datetime.date(2020, 12, 22), 'BBB', 1, 10, 0.2, 9, 100],
            [datetime.date(2021, 12, 22), 'BBB', 1, 10, 0.2, 9, 100]
            ],
            columns = ['date', 'symbol', 'open', 'high', 'low', 'close', 'volume'])
        result: pd.DataFrame = trading_view.merge_dataframes(frame1, frame2)
        self.assertEqual(list(expected.index), list(range(len(expected))))
        self.assertEqual(list(expected.index), list(result.index))
        
        diff: pd.DataFrame = expected.compare(result)
        self.assertTrue(diff.empty)

    def test_common_records_do_not_appear_twice_datetime_date(self):
        frame1: pd.DataFrame = pd.DataFrame([
            [datetime.date(2010, 12, 22), 'BBB', 1, 10, 0.2, 9, 100],
            [datetime.date(2011, 12, 22), 'BBB', 1, 10, 0.2, 9, 100],
            [datetime.date(2012, 12, 22), 'BBB', 1, 10, 0.2, 9, 100]
            ],
            columns = ['date', 'symbol', 'open', 'high', 'low', 'close', 'volume'])
        self._test_merge(frame1)
    
    def test_common_records_do_not_appear_twice_pd_Timestamp(self):
        frame1: pd.DataFrame = pd.DataFrame([
            [pd.Timestamp(year=2010, month=12, day=22), 'BBB', 1, 10, 0.2, 9, 100],
            [pd.Timestamp(year=2011, month=12, day=22), 'BBB', 1, 10, 0.2, 9, 100],
            [pd.Timestamp(year=2012, month=12, day=22), 'BBB', 1, 10, 0.2, 9, 100]
            ],
            columns = ['date', 'symbol', 'open', 'high', 'low', 'close', 'volume'])
        # adjusts timestamps to datetime.date
        trading_view.perform_data_transfomration(frame1)
        self._test_merge(frame1)
        
        