import datetime
from typing import Dict

import click
from more_itertools import difference, pairwise
from tabulate import tabulate

from .main import main
from .utils import heading
from .. import data
from ..populations import Population
from ..simulation import Simulation


headers = "keys"


def format_cell(population: Population, days: int, rate: float) -> Dict[str, str]:
    date = population.start + datetime.timedelta(days=days)
    return {
        "date": f"{date:%b %d %Y}",
        "rate": f"{rate:.2f}",
    }


def print_rates(population: Population, recovery: bool) -> None:
    if recovery:
        simulation = Simulation(population.population)
        cases = [
            simulation.feed(infections).cases
            for infections in difference(population.cases)
        ]
    else:
        cases = population.cases

    rates = [value / previous for previous, value in pairwise(cases)]
    table = [format_cell(population, days, rate) for days, rate in enumerate(rates)]
    text = f"""\
{heading(population.name)}

{tabulate(table, headers, disable_numparse=True)}
"""
    print(text)


@main.command()
@click.option("--population", "-p", default="Germany", show_default=True)
@click.option("--recovery/--no-recovery")
def rates(population: str, recovery: bool):
    _population = data.load(population)
    print_rates(_population, recovery)
