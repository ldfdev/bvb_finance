from asyncio import constants
import requests
from http import HTTPStatus
from bs4 import BeautifulSoup
import sys
import os
from pathlib import Path
from datetime import datetime
import pandas as pd
import dataclasses
import typing
import logging
from . import constants
from .ticker_formats import BVB_Ticker_Format
from persist import mongo
from . import dto

logger = logging.getLogger(__name__)

def extract_financial_reports(company_ticker):    
    print('Processing', company_ticker)
    print(constants.root_dir, constants.financial_reports, company_ticker)
    saving_location = Path(constants.root_dir) / constants.financial_reports / BVB_Ticker_Format.get_ticker(company_ticker)
    print(f'Saving location {saving_location}')
    
    saving_location.mkdir(parents=True, exist_ok=True)
    
    html_data = get_financial_reports_document_list(company_ticker)
    financial_reports = get_reports_from_html(html_data)

    financial_reports_links = [f.url for f in financial_reports]
    download_reports(saving_location, financial_reports_links)

def get_financial_reports_document_list(company_ticker) -> str:
    company_financial_data_url = constants.company_financial_data_url_template.format(ticker=company_ticker)

    company_financial_data_html_doc = requests.get(company_financial_data_url, headers=constants.company_bvb_webpage_headers)

    if HTTPStatus.OK != company_financial_data_html_doc.status_code:
        print(f'Could not company financial_data_url data for {company_financial_data_html_doc}')
        print(company_financial_data_html_doc.headers)
        print(company_financial_data_html_doc.text)
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
        # print('*')
        # print(line)
        base_document = dto.Website_Financial_Document()
        description_blob = line.find("input")
        if description_blob and  description_blob.has_attr('value'):
            base_document.description = description_blob['value']
            print("Found value", description_blob['value'])
        date_time_blob = line.find("p")
        if date_time_blob:
            date_time_blob = date_time_blob.get_text()
            date_time_format = "%d.%m.%Y %H:%M:%S"
            date_time = datetime.strptime(date_time_blob, date_time_format)
            base_document.modification_date = date_time.date()
            base_document.modification_time = date_time.time()
            
        for link in line.find_all("a"):
            if link.has_attr('href'):
                # print('Link', link['href'])
                link_document = dataclasses.replace(base_document)
                link_document.url = link['href'].lstrip('/')
                links.append(link_document)
    
    print('Following documents have been found')
    for link in links:
        print(' - ', link.file_name)

    return links

def get_company_from_html(html_doc: str) -> dto.Website_Company:
    company = dto.Website_Company()
    soup = BeautifulSoup(html_doc, 'html.parser')
    html_document_body = soup.find('body')
    for form in html_document_body.find_all('form'):
        if not form.has_attr('action'):
            continue
        form = form['action']
        company.ticker = form.lstrip('FinancialInstrumentsDetails.aspx?s=')
        break
    html_document_title = soup.find('head').find('title').get_text()
    ticker_pos = html_document_title.find(company.ticker) + len(company.ticker)
    company_name = html_document_title[ticker_pos:]
    company.name = company_name.strip()
    return company

def download_data(url):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}
    data = requests.get(url, stream = True, headers=headers)

    if HTTPStatus.OK != data.status_code:
        print(f'Dowloading {url} failed')
        print(data.headers)
        print(data.text)
        return
    return data.content

def save_data_to_disk(data, file_path):
    # SAVE the whole html page
    if Path(file_path).exists():
        print(f'File {file_path} already exsists.')
        return
    with open(file_path, 'wb') as file:
        file.write(data)

def get_downloaded_files(saving_location):
    return [x for x in Path(saving_location).iterdir() if x.is_file()]

def download_reports(saving_location, links):
    downloaded_files = get_downloaded_files(saving_location)

    new_files = [link for link in links if Path(link).name not in downloaded_files]
    
    for link in new_files:
        data = download_data(constants.download_url + link.lstrip(os.sep))
        if data is None:
            continue
        print(f'Saving {Path(link).name}')
        save_data_to_disk(data, Path(saving_location) / (Path(link).name))




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
            print(f"Scanned {dir_entry.name} and found reports: {report_files}")
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
    def search_reports_on_bvb_and_save(ticker: str) -> list[dto.Website_Financial_Document]:
        html_data = get_financial_reports_document_list(ticker)
        documents = BVB_Report.search_reports_on_bvb(ticker)
        company: dto.Website_Company  = get_company_from_html(html_data)
        company.documents = documents
        mongo.insert_website_company_document(company)

    @staticmethod
    def get_newer_reports_than_local(website_reports:list[dto.Website_Financial_Document],
                                     local_reports: list[dto.BVB_Report_Dto]) -> list[dto.Website_Financial_Document]:
        pass
    # def _filter()