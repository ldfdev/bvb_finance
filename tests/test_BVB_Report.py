import unittest
from unittest.mock import patch
import datetime
from pathlib import Path
from company_reports import dto
from company_reports import BVB_Report


BIO_data = 'bvb_company_BIO_webpage.html'
resources = 'resources'

def load_resource_file(file_name) -> str:
    with open(Path(__file__).parent / resources / file_name, 'r') as reader:
        return reader.read()

class TestBVB_Report(unittest.TestCase):
    def test_load_reports(self):
        pass
        # with patch.object(Path, 'iterdir') as mocked_iterdir:
        #     mocked_iterdir.iterdir.return_value = [

        #     ]
        #     reports = BVB_Report.load_reports()

    def test_extact_links_from_webpage(self):
        webpage = load_resource_file(BIO_data)
        reports: list[dto.Website_Financial_Document] = BVB_Report.get_reports_from_html(webpage)
        self.assertEqual(len(reports), 16)
        
        for i, r in enumerate(reports, start=1):
            print(i, r)
        self.assertEqual(reports[0].description, 'Litigii')
        self.assertEqual(reports[0].file_name, 'BIO_20240603170203_2024-06-03-Raport-Curent.pdf')
        self.assertEqual(reports[0].url, 'infocont/infocont24/{}'.format(reports[0].file_name))
        self.assertEqual(reports[0].get_modification_date(), '03-06-2024')
        self.assertEqual(reports[0].get_modification_time(), '17:05:30')

        self.assertEqual(reports[1].description, 'Litigii')
        self.assertEqual(reports[1].file_name, 'BIO_20240603170203_2024-06-03-Current-Report.pdf')
        self.assertEqual(reports[1].url, 'infocont/infocont24/{}'.format(reports[1].file_name))
        self.assertEqual(reports[1].get_modification_date(), '03-06-2024')
        self.assertEqual(reports[1].get_modification_time(), '17:05:30')

        self.assertEqual(reports[2].description, 'Raport trimestrul I 2024')
        self.assertEqual(reports[2].file_name, 'BIO_20240514180654_2024-03-31-Situa-ia-Rezultatului.pdf')
        self.assertEqual(reports[2].url, 'infocont/infocont24/{}'.format(reports[2].file_name))
        self.assertEqual(reports[2].get_modification_date(), '14-05-2024')
        self.assertEqual(reports[2].get_modification_time(), '18:11:19')

        self.assertEqual(reports[3].description, 'Raport trimestrul I 2024')
        self.assertEqual(reports[3].file_name, 'BIO_20240514180654_2024-03-31-Sumary-report.pdf')
        self.assertEqual(reports[3].url, 'infocont/infocont24/{}'.format(reports[3].file_name))
        self.assertEqual(reports[3].get_modification_date(), '14-05-2024')
        self.assertEqual(reports[3].get_modification_time(), '18:11:19')

        self.assertEqual(reports[4].description, 'Raport trimestrul I 2024')
        self.assertEqual(reports[4].file_name, 'BIO_20240514174554_2024-03-31-Situatii-financiare.pdf')
        self.assertEqual(reports[4].url, 'infocont/infocont24/{}'.format(reports[4].file_name))
        self.assertEqual(reports[4].get_modification_date(), '14-05-2024')
        self.assertEqual(reports[4].get_modification_time(), '18:11:19')

        self.assertEqual(reports[5].description, 'Raport trimestrul I 2024')
        self.assertEqual(reports[5].file_name, 'BIO_20240514174554_2024-03-31-Financial-Statements.pdf')
        self.assertEqual(reports[5].url, 'infocont/infocont24/{}'.format(reports[5].file_name))
        self.assertEqual(reports[5].get_modification_date(), '14-05-2024')
        self.assertEqual(reports[5].get_modification_time(), '18:11:19')

        self.assertEqual(reports[6].description, 'Disponibilitate raport trimestrul I 2024')
        self.assertEqual(reports[6].file_name, 'BIO_20240513142313_2024-05-14-Comunicat-disponibilitate.pdf')
        self.assertEqual(reports[6].url, 'infocont/infocont24/{}'.format(reports[6].file_name))
        self.assertEqual(reports[6].get_modification_date(), '13-05-2024')
        self.assertEqual(reports[6].get_modification_time(), '14:31:04')

        self.assertEqual(reports[7].description, 'Disponibilitate raport trimestrul I 2024')
        self.assertEqual(reports[7].file_name, 'BIO_20240513142313_2024-05-14-Communique.pdf')
        self.assertEqual(reports[7].url, 'infocont/infocont24/{}'.format(reports[7].file_name))
        self.assertEqual(reports[7].get_modification_date(), '13-05-2024')
        self.assertEqual(reports[7].get_modification_time(), '14:31:04')

        self.assertEqual(reports[8].description, 'Raport anual 2023')
        self.assertEqual(reports[8].file_name, 'BIO_20240424163807_Raport-anual-2023.pdf')
        self.assertEqual(reports[8].url, 'infocont/infocont24/{}'.format(reports[8].file_name))
        self.assertEqual(reports[8].get_modification_date(), '24-04-2024')
        self.assertEqual(reports[8].get_modification_time(), '17:29:35')

        self.assertEqual(reports[9].description, 'Raport anual 2023')
        self.assertEqual(reports[9].file_name, 'BIO_20240424171603_2024-04-24-Comunicat-disponibilitate.pdf')
        self.assertEqual(reports[9].url, 'infocont/infocont24/{}'.format(reports[9].file_name))
        self.assertEqual(reports[9].get_modification_date(), '24-04-2024')
        self.assertEqual(reports[9].get_modification_time(), '17:29:35')

        self.assertEqual(reports[10].description, 'Raport anual 2023')
        self.assertEqual(reports[10].file_name, 'BIO_20240424163801_Raport-anual-2023.zip')
        self.assertEqual(reports[10].url, 'infocont/infocont24/{}'.format(reports[10].file_name))
        self.assertEqual(reports[10].get_modification_date(), '24-04-2024')
        self.assertEqual(reports[10].get_modification_time(), '17:29:35')

        self.assertEqual(reports[11].description, 'Raport anual 2023')
        self.assertEqual(reports[11].file_name, 'BIO_20240424163747_2023-Annual-report.pdf')
        self.assertEqual(reports[11].url, 'infocont/infocont24/{}'.format(reports[11].file_name))
        self.assertEqual(reports[11].get_modification_date(), '24-04-2024')
        self.assertEqual(reports[11].get_modification_time(), '17:29:35')

        self.assertEqual(reports[12].description, 'Raport anual 2023')
        self.assertEqual(reports[12].file_name, 'BIO_20240424171603_2024-04-24-Communique-docx.pdf')
        self.assertEqual(reports[12].url, 'infocont/infocont24/{}'.format(reports[12].file_name))
        self.assertEqual(reports[12].get_modification_date(), '24-04-2024')
        self.assertEqual(reports[12].get_modification_time(), '17:29:35')

        self.assertEqual(reports[13].description, 'Raport anual 2023')
        self.assertEqual(reports[13].file_name, 'BIO_20240424163753_2023-Annual-report.zip')
        self.assertEqual(reports[13].url, 'infocont/infocont24/{}'.format(reports[13].file_name))
        self.assertEqual(reports[13].get_modification_date(), '24-04-2024')
        self.assertEqual(reports[13].get_modification_time(), '17:29:35')

        self.assertEqual(reports[14].description, 'Hotarare AGAO 24.04.2024')
        self.assertEqual(reports[14].file_name, 'BIO_20240424161834_2024-04-24-Raport-Curent.pdf')
        self.assertEqual(reports[14].url, 'infocont/infocont24/{}'.format(reports[14].file_name))
        self.assertEqual(reports[14].get_modification_date(), '24-04-2024')
        self.assertEqual(reports[14].get_modification_time(), '16:29:31')

        self.assertEqual(reports[15].description, 'Hotarare AGAO 24.04.2024')
        self.assertEqual(reports[15].file_name, 'BIO_20240424161834_2024-04-24-Current-Report.pdf')
        self.assertEqual(reports[15].url, 'infocont/infocont24/{}'.format(reports[15].file_name))
        self.assertEqual(reports[15].get_modification_date(), '24-04-2024')
        self.assertEqual(reports[15].get_modification_time(), '16:29:31')

    def test_get_company_from_html(self):
        html_doc = load_resource_file(BIO_data)
        company: dto.Website_Company = BVB_Report.get_company_from_html(html_doc)

        self.assertEqual(company.ticker, 'BIO')
        self.assertEqual(company.name, 'BIOFARM S.A.')

    def test_get_newer_reports_than_local(self):
        common_files = [
            "common_file_1",
            "common_file_2",
            "common_file_2",
            "common_file_3"
        ]

        files_present_on_disk_only = [
            "disk_file_1",
            "disk_file_1",
            "disk_file_2"
        ]

        new_files = [
            "new_file_1",
            "new_file_2"
        ]

        def create_website_financial_document(files: list[str]):
            result = []
            for file in files:
                doc = dto.Website_Financial_Document()
                doc.url = file
                result.append(doc)
            return result
        
        def create_document_dto(files: list[str]):
            result = []
            for file in files:
                doc = dto.Document_Dto()
                doc.file_name = file
                result.append(doc)
            return result
        
        website_company: dto.Website_Company = dto.Website_Company()
        website_company.ticker = 'ABC'
        website_company.documents = create_website_financial_document(common_files + new_files)

        local_report = dto.BVB_Report_Dto(ticker='abC.ro')
        local_report.documents = create_document_dto(common_files + files_present_on_disk_only)

        resulted_document = BVB_Report.BVB_Report.get_newer_reports_than_local(website_company, local_report)

        self.assertFalse(resulted_document is None)
        self.assertEqual(len(resulted_document.documents), len(new_files))
        self.assertEqual(set([doc.file_name for doc in resulted_document.documents]), set(new_files))
