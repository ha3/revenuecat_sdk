import urllib
from datetime import datetime


def encode(value: str) -> str:
    return urllib.parse.quote(value)


def datetime_to_ms(value: datetime) -> float:
    return value.timestamp() * 1000.0
