import datetime
from typing import Dict

import click
import humanize
from tabulate import tabulate

from .main import main
from .utils import heading
from .. import populations


def format_row(
    population: populations.Population, days: int, cases: int
) -> Dict[str, str]:
    date = population.start + datetime.timedelta(days)
    previous = population.cases[days - 1] if days > 0 else 0
    return {
        "date": f"{date:%b %d %Y}",
        "cases": cases,
        "cases%": f"{100 * cases / population.population:.3f}%",
        "difference": cases - previous,
        "ratio": cases / previous if previous != 0 else 0,
    }


def print_population(population: populations.Population) -> None:
    table = [
        format_row(population, days, cases)
        for days, cases in enumerate(population.cases)
    ]
    text = f"""\
{heading(population.name)}

population = {humanize.intword(population.population)}

{tabulate(table, headers="keys", floatfmt=".2f")}
"""
    print(text)


@main.command()
@click.option(
    "--population",
    "-p",
    default="Germany",
    type=click.Choice(populations.populations, case_sensitive=False,),
)
@click.option("--raw/--no-raw")
def data(population: str, raw: bool) -> None:
    if raw:
        data = populations.load_cache()
        for record in populations.load_records(data):
            print(record)
        return

    _population = populations.load(population)
    print_population(_population)
