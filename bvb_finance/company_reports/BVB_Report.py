from asyncio import constants
import requests
from http import HTTPStatus
from bs4 import BeautifulSoup
import sys
import os
import operator
from pathlib import Path
from datetime import datetime
import pandas as pd
import dataclasses
import typing
from .. import constants
from .ticker_formats import BVB_Ticker_Format
from bvb_finance.persist import mongo
from . import dto
from  bvb_finance import datetime_conventions
import bvb_finance
from bvb_finance import logging

logger = logging.getLogger()

def extract_financial_reports(company_ticker):    
    logger.info('Processing', company_ticker)
    logger.info(constants.root_dir, constants.financial_reports, company_ticker)
    saving_location = Path(constants.root_dir) / constants.financial_reports / BVB_Ticker_Format.get_ticker(company_ticker)
    logger.info(f'Saving location {saving_location}')
    
    saving_location.mkdir(parents=True, exist_ok=True)
    
    html_data = get_financial_reports_document_list(company_ticker)
    financial_reports = get_reports_from_html(html_data)

    financial_reports_links = [f.url for f in financial_reports]
    download_reports(saving_location, financial_reports_links)

def get_financial_reports_document_list(company_ticker) -> str:
    company_financial_data_url = constants.company_financial_data_url_template.format(ticker=company_ticker)

    company_financial_data_html_doc = requests.get(company_financial_data_url, headers=constants.company_bvb_webpage_headers)

    if HTTPStatus.OK != company_financial_data_html_doc.status_code:
        logger.warning(f'Could not company financial_data_url data for {company_financial_data_html_doc}')
        logger.warning(company_financial_data_html_doc.headers)
        logger.warning(company_financial_data_html_doc.text)
        sys.exit(-1)

    return company_financial_data_html_doc.text

def get_reports_from_html(html_doc: str) -> list[dto.Website_Financial_Document]:
    # SAVE the json payload from page containing all market data
    soup = BeautifulSoup(html_doc, 'html.parser')
    market_data = soup.findAll('table')

    financial_document_identofier = 'infocont24/'
    financial_data_table = None
    for table in market_data:
        if financial_document_identofier in str(table):
            financial_data_table = table
            break

    table_body = financial_data_table.find('tbody')
    links = []
    for line in table_body.findAll('td'):
        base_document = dto.Website_Financial_Document()
        description_blob = line.find("input")
        if description_blob and  description_blob.has_attr('value'):
            base_document.description = description_blob['value']
            # print("Found value", description_blob['value'])
        date_time_blob = line.find("p")
        if date_time_blob:
            date_time_blob = date_time_blob.get_text()
            date_time_format = datetime_conventions.date_time_format
            date_time = datetime.strptime(date_time_blob, date_time_format)
            base_document.modification_date = date_time.date()
            base_document.modification_time = date_time.time()
            
        for link in line.find_all("a"):
            if link.has_attr('href'):
                link_document = dataclasses.replace(base_document)
                link_document.url = link['href'].lstrip('/')
                links.append(link_document)
    
    logger.info(f'Following {len(links)} documents have been found')
    for i, link in enumerate(links, start=1):
        logger.info(f'{i:>3d}:{link.file_name}')

    return links

def extract_ticker(parser: BeautifulSoup) -> str:
    html_document_body = parser.find('body')
    for form in html_document_body.find_all('form'):
        if not form.has_attr('action'):
            continue
        form = form['action']
        return form.split('FinancialInstrumentsDetails.aspx?s=')[1]

def get_company_from_html(html_doc: str) -> dto.Website_Company:
    company = dto.Website_Company()
    soup = BeautifulSoup(html_doc, 'html.parser')
    company.ticker = extract_ticker(soup)
    html_document_title = soup.find('head').find('title').get_text()
    ticker_pos = html_document_title.find(company.ticker) + len(company.ticker)
    company_name = html_document_title[ticker_pos:]
    company.name = company_name.strip()
    return company

def get_financial_calendar_data_from_html(html_doc: str) -> list[dto.Financial_Calendar_Data]:
    logger.info('Entering get_financial_calendar_data_from_html')
    soup = BeautifulSoup(html_doc, 'html.parser')
    ticker: str = extract_ticker(soup)
    html_document_body = soup.find('body')
    documents = list()
    table_div = None
    for div in html_document_body.find_all('div'):
        h2 = div.find('h2')
        if not h2:
            continue
        if not "Calendar Financiar" in h2.get_text():
            continue
        table_div = div
        break
    logger.info(f"Found table_div element {table_div}")
    table = table_div.find('div').find('div').find('table')
    logger.info(f'Table = {table}')
    for line in table.find('tbody').findAll('td'):
        divs = [div for div in line.findAll('div')]
        logger.info(f'Table line divs {divs}')
        
        date, description = divs[:2]
        date = date.get_text().strip()
        description = description.get_text().strip()
        logger.info(f"Date <{date}> & Description <{description}>")
        months = ['ian', 'feb', 'mar', 'apr', 'mai', 'iun', 'iul', 'aug', 'sep', 'oct', 'noi', 'dec']
        day, month, year = date.split(' ')
        day = int(day)
        year = int(year)
        for i, mon in enumerate(months, start=1):
            if month.casefold().startswith(mon):
                month = i
                break
        documents.append(dto.Financial_Calendar_Data({
            "ticker": ticker,
            "date": datetime(year=year, month=month, day=day).date(),
            "description": description
        }))
    return documents

def download_data(url):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}
    data = requests.get(url, stream = True, headers=headers)

    if HTTPStatus.OK != data.status_code:
        logger.warning(f'Dowloading {url} failed')
        logger.warning(data.headers)
        logger.warning(data.text)
        return
    return data.content

def save_data_to_disk(data, file_path):
    # SAVE the whole html page
    if Path(file_path).exists():
        logger.info(f'File {file_path} already exsists.')
        return
    with open(file_path, 'wb') as file:
        file.write(data)

def get_downloaded_files(saving_location):
    return [x for x in Path(saving_location).iterdir() if x.is_file()]

def download_reports(saving_location: Path, links: list[str]) -> list[str]:
    def _files_to_str(files: list[str]) -> str:
        return '\n' + '\n'.join(files)
    
    logger.info(f"Downloading reports to {saving_location.as_posix()}")
    downloaded_files = get_downloaded_files(saving_location)

    new_files = [link for link in links if Path(link).name not in downloaded_files]
    already_downloaded_files = [link for link in links if Path(link).name not in new_files]
    
    logger.info(f"Skipping some files which are already downloaded: {_files_to_str(already_downloaded_files)}")
    logger.info(f"These new files will be downloaded: {_files_to_str(new_files)}")
    
    failures = []

    for link in new_files:
        try:
            data = download_data(constants.download_url + link.lstrip(os.sep))
            if data is None:
                continue
            logger.info(f'Saving {Path(link).name}')
            save_data_to_disk(data, Path(saving_location) / (Path(link).name))
        except Exception as exc:
            logger.warning(f"Failed to downoad {link}. Error: ", exc)
            failures.append(link)

    return failures

def load_local_report():
    reports = BVB_Report.load_reports_from_local()
    data = list()
    for report in reports:
        for doc in report.documents:
            line = [report.ticker, doc.file_name, doc.modification_date.strftime(datetime_conventions.date_format)]
            data.append(line)
    report_df = pd.DataFrame(data, columns=['Ticker', 'Report', 'Raport Date'])
    logger.debug(report_df)
    return report_df.to_dict('records')


class BVB_Report:
    @staticmethod
    def load_reports_from_local() -> list[dto.BVB_Report_Dto]:
        reports_fdlder = Path(constants.root_dir) / constants.financial_reports
        reports = list()
        for dir_entry in reports_fdlder.iterdir():
            if not dir_entry.is_dir():
                continue
            ticker = BVB_Ticker_Format.get_ticker(dir_entry.name)
            new_report = dto.BVB_Report_Dto(ticker)

            report_files = [f for f in (reports_fdlder / dir_entry.name).iterdir() if f.is_file()]
            logger.info(f"Scanned {dir_entry.name} and found reports: {report_files}")
            for rf in report_files:
                d = dto.Document_Dto.initialize(rf.name)
                
                d.disk_location = str(reports_fdlder / dir_entry.name / rf)
                new_report.documents.append(d)
            
            reports.append(new_report)
        
        return reports

    @staticmethod
    def search_reports_on_bvb(ticker: str) -> list[dto.Website_Financial_Document]:
        html_data = get_financial_reports_document_list(ticker)
        return get_reports_from_html(html_data)

    @staticmethod
    def search_report_on_bvb_and_save(ticker: str) -> dto.Website_Company:
        company: dto.Website_Company = BVB_Report.retrieve_website_company_data(ticker)
        logger.info(f"SUccessfully colelcted Website_Company for ticker {ticker}: {company}")
        mongo.insert_website_company_document(company)
        return company

    @staticmethod
    def load_reports_from_mongo() -> list[dto.Website_Company]:
        return mongo.find_all_website_company_documents()

    @staticmethod
    def retrieve_website_company_data(ticker: str) -> dto.Website_Company:
        html_data = get_financial_reports_document_list(ticker)
        mongo.insert_raw_html_document(ticker=ticker, raw_html=html_data)
        documents = BVB_Report.search_reports_on_bvb(ticker)
        company: dto.Website_Company  = get_company_from_html(html_data)
        company.documents = documents
        return company

    @staticmethod
    def get_newer_reports_than_local(website_company_data: dto.Website_Company,
                                     local_report: dto.BVB_Report_Dto) -> dto.Website_Company:
        
        if BVB_Ticker_Format.get_ticker(website_company_data.ticker) != BVB_Ticker_Format.get_ticker(local_report.ticker):
            logger.warn(f"Cannot compare company data for different tickers: website_company_data ticker {website_company_data.ticker} and local report ticker {local_report.ticker}")
            return
        old_files = set([doc.file_name for doc in local_report.documents])
        new_docs = [doc for doc in website_company_data.documents if doc.file_name not in old_files]

        new_website_company_data = dataclasses.replace(local_report)
        new_website_company_data.documents =new_docs
        return new_website_company_data
    
    @staticmethod
    def download_all_report_files(reports: typing.Iterable[dto.Website_Company]) -> list[list[str]]:
        # decide how to report failures
        # support presenting in UI the failures
        # adnd add retry button
        failures = []
        for report in reports:
            saving_location = Path(constants.root_dir) / constants.financial_reports / BVB_Ticker_Format.get_ticker(report.ticker)
            logger.info(f'Saving location {saving_location}')
    
            saving_location.mkdir(parents=True, exist_ok=True)

            files = [doc.url for doc in report.documents]

            report_failures: list[str] = download_reports(saving_location, files)

            if len(report_failures) > 0:
                failures.append([report.ticker])
                failures.append(report_failures)
        return failures

    @staticmethod
    def get_financial_calendar_data_from_html(html_doc: str) -> list[dto.Financial_Calendar_Data]:
        return get_financial_calendar_data_from_html(html_doc)
    
    @staticmethod
    def get_all_financial_calendar_data() -> list[dto.Financial_Calendar_Data]:
        html_docs: list[str] = mongo.find_raw_html_documents()
        lst = list()
        for html_doc in html_docs:
            lst.extend(get_financial_calendar_data_from_html(html_doc))
        lst.sort(key=operator.attrgetter("date", "ticker"))
        return lst
    