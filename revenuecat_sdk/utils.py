import urllib
from datetime import datetime


def encode(value: str) -> str:
    return urllib.parse.quote(value)


def to_timestamp(value: datetime) -> float:
    return value.timestamp() * 1000.0
