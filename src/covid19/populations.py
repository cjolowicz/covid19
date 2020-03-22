from dataclasses import dataclass
import datetime


@dataclass
class Population:
    name: str
    population: int
    start: datetime.date
    cases: List[int]
