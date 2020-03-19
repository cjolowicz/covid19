from dataclasses import dataclass
import datetime
from itertools import chain, count
from statistics import geometric_mean
from typing import Iterator, List, Sequence

from more_itertools import difference, pairwise

from . import data


average_case_duration = 14
probability_window_size = 5


class Simulation:
    """Simulation to predict infections."""

    def __init__(self, population: int) -> None:
        self._population: int = population
        self._cases: int = 0
        self._window: List[int] = [0] * average_case_duration
        self._probability: float = 0.0
        self._probability_window: List[int] = [0] * probability_window_size

    def feed(self, infections: int) -> int:
        """Add observed infections for a single day."""
        self._update_probability(infections)

        recoveries: int = self._window.pop(0)
        self._window.append(infections)
        self._cases += infections - recoveries

        # print(f"""FEED {infections} infections => {100 * self._probability:.2f}% probability, {recoveries} recoveries, {self._cases} cases""", end="")
        return self._cases

    def _update_probability(self, infections: int) -> None:
        if self._cases > 0:
            self._probability_window.pop(0)
            self._probability_window.append(infections / self._cases)
            if all(self._probability_window):
                self._probability = geometric_mean(self._probability_window)

    def step(self) -> int:
        """Predict infections for a single day."""
        infestation: float = self._cases / self._population
        infections: int = int(self._cases * self._probability * (1 - infestation))
        recoveries: int = self._window.pop(0)
        self._cases += infections - recoveries
        self._window.append(infections)

        # print(f"""STEP => {100 * infestation:.2f}% infestation, {infections} infections, {recoveries} recoveries, {self._cases} cases""", end="")
        return self._cases

    def run(self) -> Iterator[int]:
        """Predict infections, day by day."""
        while True:
            yield self.step()


eta = 0.0001


def converge(sequence: Sequence[int]) -> Iterator[int]:
    for previous, value in pairwise(chain([0], sequence)):
        if previous > 0 and abs(1 - value / previous) < eta:
            break
        yield value


def simulate(population: data.Population):
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
        return f"{self.days:3}  {self.date:%b %d %Y}  {self.infestation:6.2f}%  {self.cases:8}"


def print_heading(heading):
    print()
    print(heading)
    print("=" * len(heading))
    print()


def print_predictions(population: data.Population):
    print_heading(population.name)

    for days, cases in enumerate(simulate(population)):
        prediction = Prediction.create(days, population, cases)
        print(prediction)


def print_rates():
    for population in data.populations:
        print_heading(population.name)
        for days, (previous, value) in enumerate(pairwise(population.cases)):
            date = population.start + datetime.timedelta(days=days)
            rate = value / previous
            print(f"{date:%b %d %Y}  {100 * rate:.2f}%")


def run():
    for population in data.populations:
        print_predictions(population)
