import dataclasses
import typing
import datetime
import re
import logging
import pathlib

logger = logging.getLogger(__name__)

@dataclasses.dataclass
class BVB_Report_Dto:
    ticker: str
    documents: list['Document_Dto'] = dataclasses.field(default_factory=list)

@dataclasses.dataclass
class Website_Financial_Document:
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
        return self.modification_date.strftime("%d-%m-%Y")

    def get_modification_time(self):
        return self.modification_time.strftime("%H:%M:%S")
    

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
