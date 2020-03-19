import dataclasses
import datetime
from typing import Any, Dict

import click
import humanize
from tabulate import tabulate

from .main import main
from .utils import print_heading
from .. import simulation
from ..data import Population, populations


headers = [
    "days",
    "date",
    "accumulated_infections",
    "cases",
    "infections",
    "recoveries",
    "probability",
    "infestation",
]


def format_state(state: simulation.State) -> Dict[str, str]:
    result = dataclasses.asdict(state)
    for key, value in result.items():
        if isinstance(value, int):
            result[key] = humanize.intcomma(value)
        elif isinstance(value, float):
            result[key] = f"{100 * result[key]:.2f}%"
        elif isinstance(value, datetime.date):
            result[key] = humanize.naturaldate(value)
    return result


def print_predictions(population: Population) -> None:
    print_heading(population.name)

    states = [format_state(state) for state in simulation.simulate(population)]
    table = [[state[header] for header in headers] for state in states]

    print(tabulate(table, headers, stralign="right"))


@main.command()
def simulate():
    for population in populations:
        print_predictions(population)
