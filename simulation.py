from itertools import count
from statistics import geometric_mean
from typing import Iterator, List


default_case_duration = 7


class Simulation:
    """Simulation to predict infections."""

    def __init__(
        self, population: int, case_duration: int = default_case_duration,
    ) -> None:
        self.population: int = population
        self.probability: float = 0.
        self.cases: int = 0
        self.window: List[int] = [0] * case_duration

    def feed(self, infections: int) -> None:
        """Add observed infections for a single day."""
        recoveries = self.window.pop(0)
        self.window.append(infections)
        self.cases += infections - recoveries
        self.probability = geometric_mean(self.window[-5:])

    def step(self) -> None:
        """Predict infections for a single day."""
        self.cases -= self.window.pop(0)
        infestation: float = self.cases / self.population
        infections: int = int(self.cases * self.probability * (1 - infestation))
        self.window.append(infections)

    def run(self, days: int = None) -> Iterator[int]:
        """Predict infections, day by day."""
        for day in count():
            if days is not None and day >= days:
                break

            self.step()
            yield self.cases
