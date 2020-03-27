"""Data from World Bank via datasets/population."""

from collections import defaultdict
import csv
from dataclasses import dataclass
import io
from pathlib import Path
from typing import Dict, Iterator

import appdirs
import requests
import desert
import marshmallow


url = "https://raw.githubusercontent.com/datasets/population/master/data/population.csv"
cachedir = Path(appdirs.user_cache_dir(appname="covid19", appauthor="cjolowicz"))
cachefile = cachedir / "population.csv"


def load_data() -> str:
    with requests.get(url) as response:
        response.raise_for_status()
        return response.text


def update_cache() -> str:
    data = load_data()
    cachedir.mkdir(parents=True, exist_ok=True)
    with open(cachefile, mode="w") as fp:
        return fp.write(data)


def load_cache() -> str:
    if not cachefile.exists():
        update_cache()

    with open(cachefile) as fp:
        return fp.read()


@dataclass
class Record:
    country_name: str = desert.field(marshmallow.fields.Str(data_key="Country Name"))
    country_code: str = desert.field(marshmallow.fields.Str(data_key="Country Code"))
    year: int = desert.field(marshmallow.fields.Int(data_key="Year"))
    value: float = desert.field(marshmallow.fields.Float(data_key="Value"))


schema = desert.schema(Record)


def load_records(data: str) -> Iterator[Record]:
    reader = csv.DictReader(io.StringIO(data))
    for row in reader:
        try:
            yield schema.load(row)
        except marshmallow.exceptions.ValidationError as error:
            print(row, error)


def load_all() -> Dict[str, int]:
    data = load_cache()
    records = load_records(data)
    countries = defaultdict(list)
    for record in records:
        countries[record.country_name].append(record)

    def latest_value(records):
        return max(records, key=lambda record: record.year).value

    return {
        country: int(latest_value(records)) for country, records in countries.items()
    }


name_mapping = {
    "US": "United States",
}


def load(name: str) -> int:
    name = name_mapping.get(name, name)
    populations = load_all()
    return populations[name]
