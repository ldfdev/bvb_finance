import dataclasses
import datetime
import functools
import json
import typing
from bvb_finance import datetime_conventions

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        if isinstance(o, DictConverter):
            return super().encode(o._dict)
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

class SerializationObject:
    def __post_init__(self):
        # in Python an instance method and a staticmethod cannot have the same name
        # this represents a hack to be able to call serialize in both cases
        self.serialize = functools.partial(SerializationObject._serialize, self)

    @staticmethod
    def serialize(obj):
        return SerializationObject._serialize(obj)
    
    @staticmethod
    def _serialize(obj):
        str_dict = json.dumps(obj, cls=JSONEncoder, indent=4, sort_keys=True)
        return json.loads(str_dict)
    
    @staticmethod
    def deserialize(mongo_object: typing.Dict):
        raise NotImplementedError