import pandas as pd
import datetime

def get_bussiness_days_in_range(start, end) -> list[datetime.date]:
    business_days: pd.DatetimeIndex = pd.bdate_range(start, end)
    return [b_day.date() for b_day in business_days.to_pydatetime()]

def get_bussiness_days_starting_at(start, count: int) -> list[datetime.date]:
    end: datetime.date = (datetime.datetime(start.year, start.month, start.day) + datetime.timedelta(days=2 * count)).date()
    business_days: pd.DatetimeIndex = pd.bdate_range(start, end)
    return [b_day.date() for b_day in business_days.to_pydatetime()][:count]
