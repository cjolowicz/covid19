from dataclasses import dataclass
import datetime
from itertools import chain
from typing import Iterator, Sequence

import click
from more_itertools import difference, pairwise

from .main import main
from .utils import print_heading
from ..data import Population, populations
from ..simulation import Simulation


eta = 0.0001


def converge(sequence: Sequence[int]) -> Iterator[int]:
    for previous, value in pairwise(chain([0], sequence)):
        if previous > 0 and abs(1 - value / previous) < eta:
            break
        yield value


def _simulate(population: Population) -> Iterator[int]:
    simulation = Simulation(population.population)
    for infections in difference(population.cases):
        yield simulation.feed(infections)

    yield from converge(simulation.run())


@dataclass
class Prediction:
    days: int
    date: datetime.date
    cases: int
    infestation: float

    @classmethod
    def create(cls, days: int, population, cases: int):
        date = population.start + datetime.timedelta(days=days)
        infestation = min(100, 100 * cases / population.population)
        return cls(days, date, cases, infestation)

    def __str__(self):
        return "  ".join(
            (
                f"{self.days:3}",
                f"{self.date:%b %d %Y}",
                f"{self.infestation:6.2f}%",
                f"{self.cases:8}",
            )
        )


def print_predictions(population: Population) -> None:
    print_heading(population.name)

    for days, cases in enumerate(_simulate(population)):
        prediction = Prediction.create(days, population, cases)
        print(prediction)


@main.command()
def simulate():
    for population in populations:
        print_predictions(population)
