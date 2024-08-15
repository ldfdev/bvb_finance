import dataclasses
import datetime
import json
import typing
from bvb_finance import datetime_conventions

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        if isinstance(o, datetime.date):
            return o.strftime(datetime_conventions.date_format)
        if isinstance(o, datetime.time):
            return o.strftime(datetime_conventions.time_format)
        return super().default(o)
                              
class DictConverter:
    def __init__(self, d: typing.Dict):
        self._dict = d

    @property
    def dict(self):
        return self._dict
    
    def __getattr__(self, name):
        return self._dict.get(name)

    def __str__(self):
        return json.dumps(self._dict, cls=JSONEncoder, indent=4)