from collections import defaultdict
import csv
from dataclasses import dataclass
import datetime
from itertools import chain
import io
from typing import Iterator, List, Sequence, TextIO

import requests
import desert
import marshmallow as ma
from more_itertools import pairwise


@dataclass
class Population:
    name: str
    population: int
    start: datetime.date
    cases: List[int]


url = "https://opendata.arcgis.com/datasets/dd4580c810204019a7b8eb3e0b329dd6_0.csv"


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
    object_id: int = desert.field(ma.fields.Int(data_key="ObjectId"))
    state_id: int = desert.field(ma.fields.Int(data_key="IdBundesland"))
    state: str = desert.field(ma.fields.Str(data_key="Bundesland"))
    district_id: int = desert.field(ma.fields.Int(data_key="IdLandkreis"))
    district: str = desert.field(ma.fields.Str(data_key="Landkreis"))
    age_group: str = desert.field(ma.fields.Str(data_key="Altersgruppe"))
    gender: str = desert.field(ma.fields.Str(data_key="Geschlecht"))
    cases: int = desert.field(ma.fields.Int(data_key="AnzahlFall"))
    deceased: int = desert.field(ma.fields.Int(data_key="AnzahlTodesfall"))
    date: datetime.datetime = desert.field(ma.fields.DateTime(data_key="Datenstand"))
    date_reported: datetime.datetime = desert.field(
        ma.fields.DateTime(data_key="Meldedatum")
    )


schema = desert.schema(Record)


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


def _load():
    with requests.get(url) as response:
        response.encoding = None  # https://github.com/psf/requests/issues/654
        response.raise_for_status()
        fp = io.StringIO(response.text)

    records = load_records(fp)
    return list(load_populations(records))


def load(name: str = None):
    populations = _load()
    if name is None:
        return populations

    for population in populations:
        if name.lower() == population.name.lower():
            return population

    raise ValueError(f"unknown population {name}")
