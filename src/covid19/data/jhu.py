"""Data from Johns Hopkins via simonw/covid-19-datasette."""
from collections import defaultdict
from dataclasses import dataclass
import datetime
from typing import Any, Iterator, List, Optional, Sequence

import dateparser
import desert
import marshmallow
import requests

from . import populations
from ..populations import Population


url = (
    "https://covid-19.datasettes.com/covid/daily_reports.json?country_or_region={name}"
)


def request_data(name: str) -> Any:
    with requests.get(url.format(name=name)) as response:
        response.raise_for_status()
        return response.json()


class DateTime(marshmallow.fields.DateTime):
    def _deserialize(value, *args, **kwargs):
        return dateparser.parse(str(value))


@dataclass
class Record:
    rowid: int
    day: datetime.date
    country_or_region: str
    province_or_state: Optional[str]
    admin2: Optional[str]
    fips: Optional[str]
    confirmed: Optional[int]
    deaths: Optional[int]
    recovered: Optional[int]
    active: Optional[int]
    latitude: Optional[str]
    longitude: Optional[str]
    last_update: datetime.datetime = desert.field(DateTime())
    combined_key: Optional[str]


schema = desert.schema(Record)


def load_records(data: Any) -> Iterator[Record]:
    columns = data["columns"]
    for row in data["rows"]:
        try:
            mapping = dict(zip(columns, row))
            yield schema.load(mapping)
        except marshmallow.exceptions.ValidationError as error:
            raise ValueError(f"bad record: {mapping}") from error


def load_population(records: Iterator[Record]) -> Population:
    records = sorted(records, key=lambda record: record.day)
    timeseries = defaultdict(int)
    for record in records:
        timeseries[record.day] += record.confirmed
    first = records[0]
    name = first.country_or_region
    population = populations.load(name)
    cases = timeseries.values()
    return Population(name=name, population=population, start=first.day, cases=cases)


def load(name: str) -> Population:
    data = request_data(name)
    records = load_records(data)
    return load_population(records)
