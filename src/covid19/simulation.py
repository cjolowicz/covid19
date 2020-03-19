from dataclasses import dataclass, replace
import datetime
from itertools import chain
from statistics import geometric_mean
from typing import Iterator, List, Sequence

from more_itertools import difference, pairwise

from .data import Population


DAY = datetime.timedelta(days=1)
ETA = 0.0001
AVERAGE_CASE_DURATION = 14
PROBABILITY_WINDOW_SIZE = 5


@dataclass
class State:
    population: int
    date: datetime.date
    days: int = 0
    infections: int = 0
    accumulated_infections: int = 0
    recoveries: int = 0
    cases: int = 0
    infestation: float = 0.0
    probability: float = 0.0

    @classmethod
    def create(cls, population: Population) -> "State":
        return cls(population.population, population.start - DAY)

    def update(self, infections: int, recoveries: int) -> "State":
        state = replace(self)
        state.date += DAY
        state.days += 1
        state.infections = infections
        state.accumulated_infections += infections
        state.recoveries = recoveries
        state.cases += infections - recoveries
        state.infestation = state.cases / state.population
        return state

class Simulation:
    """Simulation to predict infections."""

    def __init__(self, population: Population) -> None:
        self.state: State = State.create(population)
        self.window: List[int] = [0] * AVERAGE_CASE_DURATION
        self.probability_window: List[int] = [0] * PROBABILITY_WINDOW_SIZE

    def feed(self, infections: int) -> State:
        """Add observed infections for a single day."""
        self.update_probability(infections)
        recoveries = self.window.pop(0)
        self.state = self.state.update(infections, recoveries)
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
        infections: int = int(
            self.state.cases * self.state.probability * (1 - self.state.infestation)
        )
        recoveries: int = self.window.pop(0)
        self.state = self.state.update(infections, recoveries)
        self.window.append(infections)

        return self.state

    def run(self) -> Iterator[State]:
        """Predict infections, day by day."""
        while True:
            yield self.step()


def converge(sequence: Sequence[State]) -> Iterator[State]:
    for previous, state in pairwise(chain([None], sequence)):
        if previous is not None and abs(1 - state.cases / previous.cases) < ETA:
            break
        yield state


def simulate(population: Population) -> Iterator[State]:
    simulation = Simulation(population)
    for infections in difference(population.cases):
        yield simulation.feed(infections)

    yield from converge(simulation.run())
