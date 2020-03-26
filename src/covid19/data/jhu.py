from collections import defaultdict
from dataclasses import dataclass
import datetime
from typing import Any, Iterator, List, Sequence

import dateutil.parser
import dateutil.tz
import desert
import requests

from ..populations import Population
from .api import populations


url = (
    "https://covid-19.datasettes.com/covid/daily_reports.json?country_or_region={name}"
)


def request_data(name: str) -> Any:
    with requests.get(url.format(name=name)) as response:
        response.raise_for_status()
        return response.json()


@dataclass
class Record:
    rowid: int
    day: datetime.date
    country_or_region: str
    province_or_state: Optional[str]
    admin2: Optional[str]
    fips: Optional[str]
    confirmed: int
    deaths: int
    recovered: int
    active: int
    latitude: str
    longitude: str
    last_update: datetime.datetime
    combined_key: str


schema = desert.schema(Record)


def load_records(data: Any) -> List[Record]:
    columns = data["columns"]
    return [schema.load(dict(zip(columns, row))) for row in data["rows"]]


def process_records(records: List[Record]) -> List[Record]:
    filtered = filter(lambda record: not record.province_or_state, records)
    return sorted(filtered, key=lambda record: record.day)


def load_population(records: List[Record]) -> Population:
    first = records[0]
    name = first.country_or_region
    return Population(
        name=name,
        population=populations[name],
        start=first.day,
        cases=[record.confirmed for record in records],
    )


def load(name: str) -> Population:
    data = request_data(name)
    records = load_records(data)
    records = process_records(records)
    return load_population(records)
