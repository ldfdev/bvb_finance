import unittest
from unittest.mock import patch
import datetime
from pathlib import Path
from company_reports.dto import Document_Dto
from company_reports.BVB_Report import BVB_Report

class TestBVB_Report(unittest.TestCase):
    def test_load_reports(self):
        pass
        # with patch.object(Path, 'iterdir') as mocked_iterdir:
        #     mocked_iterdir.iterdir.return_value = [

        #     ]
        #     reports = BVB_Report.load_reports()
