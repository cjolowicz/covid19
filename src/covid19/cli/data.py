import datetime
from typing import Dict

import click
import humanize
from tabulate import tabulate

from .main import main
from .utils import heading
from .. import populations


def print_population(population: populations.Population) -> None:
    table = [
        {"date": population.start + datetime.timedelta(days), "cases": cases,}
        for days, cases in enumerate(population.cases)
    ]
    text = f"""\
{heading(population.name)}

population = {humanize.intword(population.population)}
{tabulate(table, headers="keys")}
"""
    print(text)


@main.command()
@click.option(
    "--population",
    "-p",
    default="Germany",
    type=click.Choice(populations.populations, case_sensitive=False,),
)
def data(population: str):
    _population = populations.load(population)
    print_population(_population)
