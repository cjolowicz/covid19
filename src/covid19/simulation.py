from statistics import geometric_mean
from typing import Iterator, List


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
