import datetime
from typing import List, Optional

import click
import dateparser
import matplotlib.pyplot as plt
import matplotlib.dates

from . import options
from .main import main
from .. import data, simulation
from ..populations import Population


def set_aspect_ratio(ratio):
    axes = plt.gca()
    left, right = axes.get_xlim()
    bottom, top = axes.get_ylim()
    axes.set_aspect(abs((right - left) / (bottom - top)) * ratio)


def plot_predictions(
    population: Population,
    states: List[simulation.State],
    version: Optional[datetime.date],
    plots: List[str],
    output: Optional[str],
    color: str = "tab:orange",
    legend: bool = True,
    yscale: str = "linear",
) -> None:
    def percentage(value):
        return 100 * value / population.population

    if version is None:
        version = population.start + datetime.timedelta(days=len(population.cases))

    dates = [
        population.start + datetime.timedelta(days=state.days - 1) for state in states
    ]
    cases = [percentage(state.cases) for state in states]
    immune = [percentage(state.immune) for state in states]
    infections = [percentage(state.infections) for state in states]
    recoveries = [percentage(state.recoveries) for state in states]

    plt.yscale(yscale)

    if "cases" in plots:
        plt.plot(
            dates, cases, label="cases", color=color,
        )

    if "immune" in plots:
        plt.plot(
            dates, immune, label="immune", color="tab:blue",
        )

    if "infections" in plots:
        plt.plot(
            dates, infections, label="infections", color="tab:red",
        )

    if "recoveries" in plots:
        plt.plot(
            dates, recoveries, label="recoveries", color="tab:green",
        )

    title = f"""\
COVID-19 simulation for {population.name}

daily predictions based on data from RKI

{version:%b %d, %Y}"""

    plt.title(title, fontsize=10)
    plt.ylabel("% of population")
    if yscale == "linear":
        plt.ylim(bottom=-5, top=105)
    elif yscale == "log":
        plt.ylim(bottom=10 ** -4, top=10 ** 2)

    plt.grid(True)
    text = plt.figtext(
        0.99, 0.01, "https://github.com/cjolowicz/covid19", horizontalalignment="right"
    )

    if yscale == "linear":
        set_aspect_ratio(0.4)

    if legend:
        plt.legend()

    locator = matplotlib.dates.MonthLocator()
    formatter = matplotlib.dates.DateFormatter("%b")
    xaxis = plt.gca().xaxis
    xaxis.set_major_locator(locator)
    xaxis.set_major_formatter(formatter)

    if output is None:
        plt.show()
    else:
        plt.savefig(output)

    text.remove()


@main.command()
@options.population
@click.option("--plot-cases/--no-plot-cases", default=True)
@click.option("--plot-immune/--no-plot-immune", default=False)
@click.option("--plot-infections/--no-plot-infections", default=False)
@click.option("--plot-recoveries/--no-plot-recoveries", default=False)
@options.yscale
@click.option("--date", metavar="DATE", help="Base simulation on data as of DATE")
@options.with_immunity
@click.option("--output", "-o", metavar="FILE")
def plot(
    population: str,
    plot_cases: bool,
    plot_immune: bool,
    plot_infections: bool,
    plot_recoveries: bool,
    yscale: str,
    date: Optional[str],
    with_immunity: bool,
    output: Optional[str],
):
    _population = data.load(population)
    version = dateparser.parse(date).date() if date is not None else None
    states = simulation.simulate(_population, with_immunity, version)
    plots = sum(
        [
            ["cases"] if plot_cases else [],
            ["immune"] if plot_immune else [],
            ["infections"] if plot_infections else [],
            ["recoveries"] if plot_recoveries else [],
        ],
        start=[],
    )
    plot_predictions(
        population=_population,
        states=list(states),
        version=version,
        plots=plots,
        output=output,
        yscale=yscale,
    )
