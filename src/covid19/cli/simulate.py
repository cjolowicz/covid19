import dataclasses
from typing import Dict

import click
from tabulate import tabulate

from .main import main
from .utils import print_heading
from .. import simulation
from ..data import Population, populations


def print_predictions(population: Population) -> None:
    print_heading(population.name)

    headers = [
        "days",
        "date",
        "accumulated_infections",
        "infestation",
        "cases",
        "recoveries",
        "probability",
        "infections",
    ]
    states = [dataclasses.asdict(state) for state in simulation.simulate(population)]
    table = [[state[header] for header in headers] for state in states]

    print(tabulate(table, headers, floatfmt=".2f"))


@main.command()
def simulate():
    for population in populations:
        print_predictions(population)
