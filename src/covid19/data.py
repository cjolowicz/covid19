from dataclasses import dataclass
import datetime
from typing import List


last_updated = datetime.date.fromisoformat("2020-03-18")


@dataclass
class Population:
    name: str
    population: int
    start: datetime.date
    cases: List[int]


berlin = Population(
    name="Berlin",
    population=3_700_000,
    start=datetime.date.fromisoformat("2020-03-02"),
    cases=[1, 3, 6, 9, 15, 24, 28, 40, 48, 90, 137, 174, 216, 265, 300, 345, 391],
)

germany = Population(
    name="Germany",
    population=82_900_000,
    start=datetime.date.fromisoformat("2020-02-24"),
    cases=[
        16,
        18,
        21,
        26,
        53,
        66,
        117,
        150,
        188,
        242,
        354,
        534,
        684,
        847,
        1112,
        1460,
        1884,
        2369,
        3062,
        3795,
        4838,
        6012,
        7156,
        8198,
    ],
)

populations = berlin, germany
