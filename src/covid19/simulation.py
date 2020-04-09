from dataclasses import dataclass, replace
import datetime
from itertools import chain, islice
from statistics import geometric_mean
from typing import Iterator, List, Sequence

from more_itertools import difference, pairwise

from .populations import Population


ETA = 0.0001
AVERAGE_CASE_DURATION = 14
PROBABILITY_WINDOW_SIZE = 7


@dataclass
class State:
    days: int = 0
    infections: int = 0
    recoveries: int = 0
    cases: int = 0
    immune: int = 0
    probability: float = 0.0

    def update(
        self, infections: int, recoveries: int, with_immunity: bool = True
    ) -> None:
        state = replace(self)
        state.days += 1
        state.infections = infections
        state.recoveries = recoveries
        state.cases += infections - recoveries
        state.immune += recoveries if with_immunity else 0
        return state


class Simulation:
    """Simulation to predict infections."""

    def __init__(self, population: int, with_immunity: bool = True) -> None:
        self.population = population
        self.state = State()
        self.window: List[int] = [0] * AVERAGE_CASE_DURATION
        self.probability_window: List[int] = [0] * PROBABILITY_WINDOW_SIZE
        self.with_immunity = with_immunity

    def feed(self, infections: int) -> State:
        """Add observed infections for a single day."""
        self.update_probability(infections)
        recoveries = self.window.pop(0)
        self.state = self.state.update(infections, recoveries, self.with_immunity)
        self.window.append(infections)

        return self.state

    def update_probability(self, infections: int) -> None:
        if self.state.cases > 0:
            self.probability_window.pop(0)
            self.probability_window.append(infections / self.state.cases)
            if all(self.probability_window):
                self.state.probability = geometric_mean(self.probability_window)

    def step(self) -> State:
        """Predict infections for a single day."""
        immunization: float = self.state.immune / self.population
        infestation: float = self.state.cases / self.population
        infections: int = int(
            self.state.cases
            * self.state.probability
            * (1 - (infestation + immunization))
        )
        recoveries: int = self.window.pop(0)
        self.state = self.state.update(infections, recoveries, self.with_immunity)
        self.window.append(infections)

        return self.state

    def run(self) -> Iterator[State]:
        """Predict infections, day by day."""
        while True:
            yield self.step()


def converge(sequence: Sequence[State]) -> Iterator[State]:
    for previous, state in pairwise(chain([None], sequence)):
        if previous is not None and (
            previous.cases == 0 or abs(1 - state.cases / previous.cases) < ETA
        ):
            break
        yield state


def simulate(
    population: Population,
    with_immunity: bool = True,
    version: datetime.date = None,
    end: datetime.date = None,
) -> Iterator[State]:
    cases = (
        population.cases
        if version is None
        else (population.cases[: (version - population.start).days + 1])
    )
    simulation = Simulation(population.population, with_immunity)
    for infections in difference(cases):
        yield simulation.feed(infections)

    if end is not None:
        stop = (end - population.start).days + 1
        yield from islice(simulation.run(), stop)

    yield from converge(simulation.run())
