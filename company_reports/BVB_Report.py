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
from . import dto

logger = logging.getLogger(__name__)

def extract_financial_reports(company_ticker):    
    print('Processing', company_ticker)
    print(constants.root_dir, constants.financial_reports, company_ticker)
    saving_location = Path(constants.root_dir) / constants.financial_reports / BVB_Ticker_Format.get_ticker(company_ticker)
    print(f'Saving location {saving_location}')
    
    saving_location.mkdir(parents=True, exist_ok=True)
    
    html_data = get_financial_reports_document_list(company_ticker)
    financial_reports_links = get_reports_from_html(html_data)    
    download_reports(saving_location, financial_reports_links)

def get_financial_reports_document_list(company_ticker):
    company_financial_data_url = constants.company_financial_data_url_template.format(ticker=company_ticker)

    company_financial_data_html_doc = requests.get(company_financial_data_url, headers=constants.company_bvb_webpage_headers)

    if HTTPStatus.OK != company_financial_data_html_doc.status_code:
        print(f'Could not company financial_data_url data for {company_financial_data_html_doc}')
        print(company_financial_data_html_doc.headers)
        print(company_financial_data_html_doc.text)
        sys.exit(-1)

    return company_financial_data_html_doc

def get_reports_from_html(html_doc):
    # SAVE the json payload from page containing all market data
    soup = BeautifulSoup(html_doc.text, 'html.parser')
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
        for link in line.find_all("a"):
            if link.has_attr('href'):
                # print('Link', link['href'])
                links.append(link['href'].lstrip('/'))
    
    print('Following documents have been found')
    for link in links:
        print(' - ', Path(link).name)

    return links

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
    def search_reports_on_bvb(ticker: str):
        html_data = get_financial_reports_document_list(ticker)
        financial_reports_links = get_reports_from_html(html_data)  