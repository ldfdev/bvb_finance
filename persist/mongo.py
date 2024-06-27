from pymongo import MongoClient
from . import db_constants
from bvb_finance.company_reports import dto
import logging

__all__ = [
    'insert_website_company_document'
]

logger = logging.getLogger(__name__)

client = MongoClient("localhost", 27017)

db = client[db_constants.bvb_companies_db_name]

bvb_companies_collection = db[db_constants.bvb_companies_collection]

def insert_website_company_document(company_data: dto.Website_Company):
    db_document: dto.Website_Company = bvb_companies_collection.find_one({'ticker': company_data.ticker})
    if (db_document is None):
        bvb_companies_collection.insert_one(company_data.serialize())
        return
    docs = [doc for doc in company_data.documents if doc not in db_document.documents]
    db_document.documents.extend(docs)
    logger.info('Serializing', db_document.serialize())
    bvb_companies_collection.save(db_document.serialize())

