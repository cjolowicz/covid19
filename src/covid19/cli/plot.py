import matplotlib.pyplot as plt

import click

from .main import main
from .. import data, simulation


def plot_predictions(population: data.Population, with_immunity: bool) -> None:
    def percentage(value):
        return 100 * value / population.population

    states = list(simulation.simulate(population, with_immunity))
    plt.title(population.name)
    plt.xlabel("days")
    plt.ylabel("% of population")
    plt.grid(True)
    plt.plot([percentage(state.cases) for state in states], label="cases")
    plt.plot([percentage(state.immune) for state in states], label="immune")
    plt.plot([percentage(state.infections) for state in states], label="infections")
    plt.plot([percentage(state.recoveries) for state in states], label="recoveries")
    plt.legend()
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
