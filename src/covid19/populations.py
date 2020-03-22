from collections import defaultdict
import csv
from dataclasses import dataclass
import datetime
from itertools import chain
import io
from pathlib import Path
from typing import Iterator, List, Sequence, TextIO

import appdirs
import dateutil.tz
import requests
import marshmallow as ma
from more_itertools import pairwise


url = "https://opendata.arcgis.com/datasets/dd4580c810204019a7b8eb3e0b329dd6_0.csv"
cachedir = Path(appdirs.user_cache_dir(appname="covid19", appauthor="cjolowicz"))
cachefile = cachedir / "covid19.csv"


@dataclass
class Population:
    name: str
    population: int
    start: datetime.date
    cases: List[int]


# https://de.wikipedia.org/wiki/Liste_der_deutschen_Bundesl%C3%A4nder_nach_Bev%C3%B6lkerung
populations = {
    "Baden-Württemberg": 11_069_533,
    "Bayern": 13_076_721,
    "Berlin": 3_644_826,
    "Brandenburg": 2_511_917,
    "Bremen": 682_986,
    "Hamburg": 1_841_179,
    "Hessen": 6_265_809,
    "Mecklenburg-Vorpommern": 1_609_675,
    "Niedersachsen": 7_982_448,
    "Nordrhein-Westfalen": 17_932_651,
    "Rheinland-Pfalz": 4_084_844,
    "Saarland": 990_509,
    "Sachsen": 4_077_937,
    "Sachsen-Anhalt": 2_208_321,
    "Schleswig-Holstein": 2_896_712,
    "Thüringen": 2_143_145,
    "-nicht erhoben-": 1,
}

populations["Germany"] = sum(populations.values())


@dataclass
class Record:
    object_id: int
    state_id: int
    state: str
    district_id: int
    district: str
    age_group: str
    gender: str
    cases: int
    deceased: int
    date: datetime.datetime
    version: datetime.datetime


class RecordSchema(ma.Schema):
    object_id = ma.fields.Int(data_key="ObjectId")
    state_id = ma.fields.Int(data_key="IdBundesland")
    state = ma.fields.Str(data_key="Bundesland")
    district_id = ma.fields.Int(data_key="IdLandkreis")
    district = ma.fields.Str(data_key="Landkreis")
    age_group = ma.fields.Str(data_key="Altersgruppe")
    gender = ma.fields.Str(data_key="Geschlecht")
    cases = ma.fields.Int(data_key="AnzahlFall")
    deceased = ma.fields.Int(data_key="AnzahlTodesfall")
    date = ma.fields.DateTime(data_key="Meldedatum")
    version = ma.fields.DateTime(data_key="Datenstand", format="%d.%m.%Y %H:%M")

    @ma.post_load
    def post_load(self, data, **kwargs):
        return Record(**data)


schema = RecordSchema()


def load_records(data: str) -> Iterator[Record]:
    reader = csv.DictReader(io.StringIO(data))
    for row in reader:
        if row["IdLandkreis"] == "0-1":
            row["IdLandkreis"] = "-1"
        if "Empfagen" in row:
            del row["Empfagen"]
        try:
            yield schema.load(row)
        except ma.exceptions.ValidationError as error:
            print(row, error)


def load_populations(records: Sequence[Record]) -> Iterator[Population]:
    table = defaultdict(lambda: defaultdict(int))
    for record in records:
        table[record.state][record.date] += record.cases
        table["Germany"][record.date] += record.cases

    for state, points in table.items():
        dates = sorted(points)
        population = Population(
            name=state, population=populations[state], start=dates[0].date(), cases=[]
        )

        cases = 0
        for previous, date in pairwise(chain([None], dates)):
            if previous is not None:
                for _ in range((date - previous).days - 1):
                    population.cases.append(cases)

            cases += points[date]
            population.cases.append(cases)

        yield population


def load_data() -> str:
    with requests.get(url) as response:
        response.encoding = None  # https://github.com/psf/requests/issues/654
        response.raise_for_status()
        return response.text


def update_cache() -> str:
    data = load_data()
    cachedir.mkdir(parents=True, exist_ok=True)
    with open(cachefile, mode="w") as fp:
        return fp.write(data)


def is_cache_outdated() -> bool:
    if not cachefile.exists():
        return True

    tz = dateutil.tz.gettz()
    mtime = cachefile.stat().st_mtime
    last_updated = datetime.datetime.fromtimestamp(mtime, tz=tz).date()

    return datetime.datetime.now(tz=tz).date() > last_updated


def load_cache() -> str:
    if is_cache_outdated():
        update_cache()

    with open(cachefile) as fp:
        return fp.read()


def _load():
    data = load_cache()
    records = load_records(data)
    return list(load_populations(records))


def load(name: str = None):
    populations = _load()
    if name is None:
        return populations

    for population in populations:
        if name.lower() == population.name.lower():
            return population

    raise ValueError(f"unknown population {name}")
