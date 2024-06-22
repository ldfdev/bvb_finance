import unittest
import datetime
from company_reports.dto import Document_Dto

class TestDocument_Dto(unittest.TestCase):
    def test_initialization(self):
        valid_file_name = 'AQ_20240520180453_AQ-Anun-disponibilitate-nregistrare-teleconferin-rezulta.pdf'

        doc: Document_Dto = Document_Dto.initialize(valid_file_name)

        self.assertEqual(doc.modification_date, datetime.date(2024, 5, 20))
        self.assertEqual(doc.modification_time, datetime.time(18, 4, 53))
        self.assertEqual(doc.file_name, valid_file_name)

    def test_initialization_default_time(self):
        valid_file_name = 'AQ_20240430_-164532_1223-ro-Audit-report-Separate-FS-PIE-Aquila.pdf'

        doc: Document_Dto = Document_Dto.initialize(valid_file_name)

        self.assertEqual(doc.modification_date, datetime.date(2024, 4, 30))
        self.assertEqual(doc.modification_time, datetime.time(0, 0, 0))
        self.assertEqual(doc.file_name, valid_file_name)


if __name__ == '__main__':
    unittest.main()