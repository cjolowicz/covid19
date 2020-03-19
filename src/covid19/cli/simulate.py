import click

from .main import main
from .utils import print_heading
from .. import simulation
from ..data import Population, populations


def print_predictions(population: Population) -> None:
    print_heading(population.name)
    print()
    print(
        "  ".join(
            (
                "DAY",
                f"{'DATE':12}",
                f"{'INFEST':6}%",
                f"{'CASES':8}",
                f"{'ACC     ':8}",
            )
        )
    )

    for state in simulation.simulate(population):
        print(
            "  ".join(
                (
                    f"{state.days:3}",
                    f"{state.date:%b %d %Y}",
                    f"{state.infestation:6.2f}%",
                    f"{state.cases:8}",
                    f"{state.accumulated_infections:8}",
                )
            )
        )


@main.command()
def simulate():
    for population in populations:
        print_predictions(population)
