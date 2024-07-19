from pymongo import MongoClient
from . import db_constants
from bvb_finance.company_reports import dto
from bvb_finance import logging
import typing
import bvb_finance

__all__ = [
    'insert_website_company_document',
    'find_one_website_company_document',
    'find_all_website_company_documents',
]

logger = logging.getLogger()

client = MongoClient("localhost", 27017)

db = client[db_constants.bvb_companies_db_name]

bvb_companies_collection = db[db_constants.bvb_companies_collection]

def insert_website_company_document(company_data: dto.Website_Company):
    company_data_dict = company_data.serialize()
    # actually db_document is plain Python dict
    db_document: typing.Dict = bvb_companies_collection.find_one({'ticker': company_data.ticker})
    if (db_document is None):
        logger.info(f"Inserting new document {company_data_dict}")
        bvb_companies_collection.insert_one(company_data_dict)
        return
    docs = [doc for doc in company_data_dict['documents'] if doc not in db_document['documents']]
    if len(docs) > 0:
        logger.info("Updating ticker: {} description: {} with documents: {}".format(
            company_data_dict.get('ticker', 'No ticker available'),
            company_data_dict.get('name', 'No name available'),
            docs,
        ))
    db_document['documents'].extend(docs)
    bvb_companies_collection.update_one({"_id": db_document["_id"]}, { "$set": { 'documents': db_document['documents'] } })

def find_one_website_company_document(ticker: str) -> typing.Optional[dto.Website_Company]:
    db_document: typing.Dict = bvb_companies_collection.find_one({'ticker': ticker})
    if db_document is None:
        return None
    return dto.Website_Company.deserialize(db_document)

def find_all_website_company_documents() -> list[dto.Website_Company]:
    db_documents: list[typing.Dict] = bvb_companies_collection.find({})
    return [dto.Website_Company.deserialize(db_document) for db_document in db_documents]
