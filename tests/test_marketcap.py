import unittest
import logging
import datetime
from bvb_finance.marketcap import dto as marketcapdto
from bvb_finance.marketcap import bvb_radar
from . import load_resource_file

logger = logging.getLogger(__name__)

class TestMarketcap(unittest.TestCase):
    def test_CompanyMarketCap_conversion_from_str(self):
        raw_str_company_market_cap_data = load_resource_file("marketcap_record_instance.json")

        company: marketcapdto.CompanyMarketCap = marketcapdto.CompanyMarketCap.from_str(raw_str_company_market_cap_data)
        # company_dict
       
        self.assertEqual(company.simbol, "H2O")
        self.assertEqual(company.nume,"SOCIETATEA DE PRODUCERE A ENERGIEI ELECTRICE IN HIDROCENTRALE  HIDROELECTRICA S.A.")
        self.assertEqual(company.pret, "127,4000")
        self.assertEqual(company.capitalizare, 57304847036)
        self.assertEqual(company.divy, "13,990000")
        self.assertEqual(company.anDividenend, "07.06.2024")
        self.assertEqual(company.divyAnual, "10,98")
        self.assertEqual(company.volum1y, "44.205.018")
        self.assertEqual(company.var1y, "")
        self.assertEqual(company.var7d, "2,08")
        self.assertEqual(company.var1sapt, "0,39")
        self.assertEqual(len(company.evolutie), 4)

    def test_parse_market_cap_data(self):
        raw_str_company_market_cap_webpage = load_resource_file("bvb_companies_by_market_cap.html")
        companies: list[marketcapdto.CompanyMarketCap] = bvb_radar.parse_market_cap_data(raw_str_company_market_cap_webpage)

        self.assertEqual(len(companies), 84)

        pandas_data = bvb_radar.convert_market_cap_data_to_df(companies)
        self.assertEqual(len(pandas_data), 84)
        for dict_ in pandas_data:
            self.assertIn('Ticker', dict_.keys())
            self.assertIn('Nume', dict_.keys())
            self.assertIn('Pret', dict_.keys())
            self.assertIn('Capitalizare', dict_.keys())
            self.assertIn('Var 7 zile', dict_.keys())

    def test_parse_market_cap_modification_date(self):
        raw_str_company_market_cap_webpage = load_resource_file("bvb_companies_by_market_cap.html")
        data: datetime.datetime = bvb_radar.parse_market_cap_modification_date(raw_str_company_market_cap_webpage)
        self.assertEqual(data.year, 2024)
        self.assertEqual(data.month, 7)
        self.assertEqual(data.day, 9)
        self.assertEqual(data.hour, 15)
        self.assertEqual(data.minute, 23)
        self.assertEqual(data.second, 34)