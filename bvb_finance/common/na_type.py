
NAType = "N/A"

def na_type_check(func):
    def wrapper(*args, **kwargs):
        if contains_na_type(*args):
            return NAType
        if contains_na_type(*kwargs.values()):
            return NAType
        return func(*args, **kwargs)
        
    return wrapper

def contains_na_type(*types):
    return any(is_na_type(type_) for type_ in types)

def is_na_type(value_) -> bool:
    return value_ == NAType