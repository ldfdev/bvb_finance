import datetime

date_format="%d.%m.%Y"
time_format="%H:%M:%S"
date_time_format = f"{date_format} {time_format}"
date_time_file_format = date_time_format.replace(' ', '_')

def to_bvb_finance_date_format(date: datetime.date | str) -> str:
    if isinstance(date, str):
        return date
    return date.strftime(date_format)

def datetime_to_string(o):
    if isinstance(o, datetime.date):
        return o.strftime(date_format)
    if isinstance(o, datetime.datetime):
        return o.date().strftime(date_format)
    if isinstance(o, datetime.time):
        return o.strftime(time_format)
    return o
