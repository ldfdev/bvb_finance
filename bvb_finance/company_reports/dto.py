import dataclasses, json
import typing
import datetime
import re
from bvb_finance import logging
import pathlib

from bvb_finance import datetime_conventions
from bvb_finance.common import dto as common_dto

logger = logging.getLogger()


@dataclasses.dataclass
class BVB_Report_Dto:
    ticker: str
    documents: list['Document_Dto'] = dataclasses.field(default_factory=list)

@dataclasses.dataclass
class Website_Financial_Document(common_dto.SerializationObject):
    description: str = None
    url: str = None
    modification_date: datetime.date = None
    modification_time: datetime.time = None

    @property
    def file_name(self) -> str:
        if not self.url:
            return None
        return pathlib.Path(self.url).name
    
    def get_modification_date(self):
        return self.modification_date.strftime(datetime_conventions.date_format)

    def get_modification_time(self):
        return self.modification_time.strftime(datetime_conventions.time_format)

    @staticmethod
    def deserialize(mongo_object: typing.Dict) -> 'Website_Financial_Document':
        py_object = Website_Financial_Document()
        py_object.description = mongo_object['description']
        date_time_f = "%Y-%m-%d%H:%M:%S"
        date_time_obj: datetime.datetime = datetime.datetime.strptime(mongo_object['modification_date'] + mongo_object['modification_time'],
                                                                      date_time_f)
        py_object.modification_date = date_time_obj.date()
        py_object.modification_time = date_time_obj.time()
        py_object.url = mongo_object['url']
        return py_object

@dataclasses.dataclass
class Website_Company(common_dto.SerializationObject):
    name: str = None
    ticker: str = None
    documents: list[Website_Financial_Document] = dataclasses.field(default_factory=list)

    @staticmethod
    def deserialize(mongo_object: typing.Dict) -> 'Website_Company':
        py_object = Website_Financial_Document()
        py_object.name = mongo_object['name']
        py_object.ticker = mongo_object['ticker']
        py_object.documents = [
            Website_Financial_Document.deserialize(serialized)
            for serialized in mongo_object['documents']
        ]
        return py_object

@dataclasses.dataclass
class Document_Dto:
    file_name: str = None
    disk_location: str = None
    resource_url: str = None
    modification_date: datetime.date = None
    modification_time: datetime.time = None

    @staticmethod
    def initialize(file_name: str, resource_url: str = None) -> 'Document_Dto':
        # AQ_20240520180453_AQ-Anun-disponibilitate-nregistrare-teleconferin-rezulta.pdf

        doc = Document_Dto()
        doc.file_name = file_name
        doc.resource_url = resource_url

        date_time = str()
        match = re.search("[\d]+", file_name)
        if match is None:
            logger.error(f"Cannot detect date tiem from file name {file_name}")
        else:
            date_time = match.group(0)
        year, month, day, hour, min, sec = [None] * 6
        default_hour = 00
        default_minute = 00
        default_second = 00
        
        try:
            year = int(date_time[:4])
            month = int(date_time[4:6])
            day = int(date_time[6:8])
            hour = int(date_time[8:10])
            min = int(date_time[10:12])
            sec = int(date_time[12:14])
        except (IndexError, ValueError)  as ie:
            failed_at = None
            if year is None:
                failed_at = 'year'
            elif month is None:
                failed_at = 'month'
            elif day is None:
                failed_at = 'day'
            elif hour is None:
                failed_at = 'hour'
                hour, min, sec = default_hour, default_minute, default_second
            elif min is None:
                failed_at = 'minute'
                min = default_minute
                sec = default_second
            elif sec is None:
                failed_at = 'second'
                sec = default_second

            logger.error(f'Failed to parse date time component {failed_at} from <<{date_time} - {file_name}>>. Will use default value')
        
        if None in [year, month, day]:
            logger.error(f"Using today as modification date for document {file_name}")
            doc.modification_date = datetime.datetime.now().date()
            hour, min, sec = default_hour, default_minute, default_second
        else:
            doc.modification_date = datetime.date(year, month, day)
        doc.modification_time = datetime.time(hour, min, sec)

        return doc

class Financial_Calendar_Data_Dict(typing.Dict):
    ticker: str
    date: datetime.date
    description: str

class Financial_Calendar_Data(common_dto.DictConverter):
    pass