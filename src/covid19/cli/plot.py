import datetime

import click
import matplotlib.pyplot as plt
import matplotlib.dates

from .main import main
from .. import data, simulation


def plot_predictions(population: data.Population, with_immunity: bool) -> None:
    def percentage(value):
        return 100 * value / population.population

    states = list(simulation.simulate(population, with_immunity))
    last_updated = population.start + datetime.timedelta(days=len(population.cases))
    dates = [
        population.start + datetime.timedelta(days=state.days - 1) for state in states
    ]
    cases = [percentage(state.cases) for state in states]
    immune = [percentage(state.immune) for state in states]
    infections = [percentage(state.infections) for state in states]
    recoveries = [percentage(state.recoveries) for state in states]

    plt.plot(
        dates, cases, label="cases", color="tab:orange",
    )
    plt.plot(
        dates, immune, label="immune", color="tab:blue",
    )
    plt.plot(
        dates, infections, label="infections", color="tab:red",
    )
    plt.plot(
        dates, recoveries, label="recoveries", color="tab:green",
    )

    plt.suptitle(f"COVID-19 simulation for {population.name}", fontsize=14)
    plt.title(f"Last updated: {last_updated:%b %d, %Y}", fontsize=10)
    plt.ylabel("% of population")
    plt.grid(True)
    plt.legend()

    locator = matplotlib.dates.MonthLocator()
    formatter = matplotlib.dates.DateFormatter("%b")
    xaxis = plt.gca().xaxis
    xaxis.set_major_locator(locator)
    xaxis.set_major_formatter(formatter)

    plt.show()


@main.command()
@click.option(
    "--population",
    "-p",
    default="Germany",
    type=click.Choice([population.name for population in data.populations]),
)
@click.option("--immunity/--no-immunity", "with_immunity", default=True)
def plot(population: str, with_immunity: bool):
    _population: data.Population = data.find(population)
    plot_predictions(_population, with_immunity)
