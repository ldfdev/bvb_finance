import numbers
import typing

def safe_sum(items: typing.Iterable[numbers.Number]) -> numbers.Number:
    items_ = (item for item in items if isinstance(item, numbers.Number))
    return sum(items_)

def safe_prod(a: numbers.Number, b: numbers.Number) -> numbers.Number:
    if not all(isinstance(x, numbers.Number) for x in (a, b)):
        return "N/A"
    return a * b