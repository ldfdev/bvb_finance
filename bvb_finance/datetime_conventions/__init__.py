import datetime

date_format="%d.%m.%Y"
time_format="%H:%M:%S"
date_time_format = f"{date_format} {time_format}"
date_time_file_format = date_time_format.replace(' ', '_')

def to_bvb_finance_date_format(date: datetime.date | str) -> str:
    if isinstance(date, str):
        return date
    return date.strftime(date_format)