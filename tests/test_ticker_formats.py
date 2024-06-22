import unittest
from company_reports.ticker_formats import BVB_Ticker_Format

class TestTickerFormats(unittest.TestCase):
    def test_BVB_Ticker_Format_new_ticker(self):
        ticker = BVB_Ticker_Format.get_ticker('BIO')
        self.assertEqual(ticker, 'BIO.RO')
    
    def test_BVB_Ticker_Format_correct_ticker(self):
        ticker = BVB_Ticker_Format.get_ticker('BIO.RO')
        self.assertEqual(ticker, 'BIO.RO')
    