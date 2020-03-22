from collections import defaultdict
from dataclasses import dataclass
import datetime
from typing import Any, Iterator, List, Sequence

import dateutil.parser
import dateutil.tz
import requests

from ..populations import Population


url = "https://covid19-germany.appspot.com/timeseries/{state}/cases"

iso_3166_2_de_reverse = {
    "DE-BW": "Baden-Württemberg",
    "DE-BY": "Bayern",
    "DE-BE": "Berlin",
    "DE-BB": "Brandenburg",
    "DE-HB": "Bremen",
    "DE-HH": "Hamburg",
    "DE-HE": "Hessen",
    "DE-MV": "Mecklenburg-Vorpommern",
    "DE-NI": "Niedersachsen",
    "DE-NW": "Nordrhein-Westfalen",
    "DE-RP": "Rheinland-Pfalz",
    "DE-SL": "Saarland",
    "DE-SN": "Sachsen",
    "DE-ST": "Sachsen-Anhalt",
    "DE-SH": "Schleswig-Holstein",
    "DE-TH": "Thüringen",
}
iso_3166_2_de = {value: key for key, value in iso_3166_2_de_reverse.items()}


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
}

populations["Germany"] = sum(populations.values())


@dataclass
class Record:
    datetime: datetime.datetime
    cases: int


def request_data(name: str) -> Any:
    code = iso_3166_2_de[name]
    with requests.get(url.format(state=code)) as response:
        response.raise_for_status()
        return response.json()


def load_records(name: str) -> Iterator[Record]:
    data = request_data(name)
    for entry in data["data"]:
        for date, cases in entry.items():
            yield Record(
                datetime=dateutil.parser.isoparse(date), cases=int(cases),
            )


def aggregate(records: Sequence[Record]) -> List[Record]:
    timeseries = defaultdict(int)
    for record in records:
        utctime = record.datetime.astimezone(tz=dateutil.tz.UTC)
        utcdate = datetime.datetime.combine(utctime.date(), datetime.time())
        timeseries[utcdate] += record.cases
    return [
        Record(datetime=timestamp, cases=timeseries[timestamp])
        for timestamp in sorted(timeseries)
    ]


def load_population(name: str, records: List[Record]) -> Population:
    return Population(
        name=name,
        population=populations[name],
        start=records[0].datetime.date(),
        cases=[record.cases for record in records],
    )


def load_state(name: str) -> Population:
    records = load_records(name)
    records = aggregate(records)
    return load_population(name, records)


def load_germany() -> Population:
    records = aggregate(
        record for name in iso_3166_2_de for record in load_records(name)
    )
    return load_population("Germany", records)


def load(name: str) -> Population:
    if name.lower() == "germany":
        return load_germany()

    return load_state(name)
