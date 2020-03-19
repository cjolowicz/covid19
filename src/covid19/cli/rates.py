import datetime

import click
from more_itertools import difference, pairwise

from .main import main
from .utils import heading
from ..data import Population, populations
from ..simulation import Simulation


def print_rates(population: Population, recovery: bool) -> None:
    print()
    print(heading(population.name))
    print()

    if recovery:
        simulation = Simulation(population.population)
        cases = [
            simulation.feed(infections).cases
            for infections in difference(population.cases)
        ]
    else:
        cases = population.cases

    for days, (previous, value) in enumerate(pairwise(cases)):
        date = population.start + datetime.timedelta(days=days)
        rate = value / previous
        print(f"{date:%b %d %Y}  {100 * rate:.2f}%")


@main.command()
@click.option("--recovery/--no-recovery")
def rates(recovery: bool):
    for population in populations:
        print_rates(population, recovery)
