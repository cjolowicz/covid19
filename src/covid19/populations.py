from dataclasses import dataclass
import datetime
from typing import List


@dataclass
class Population:
    name: str
    population: int
    start: datetime.date
    cases: List[int]
