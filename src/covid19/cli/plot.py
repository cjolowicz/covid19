import matplotlib.pyplot as plt

import click

from .main import main
from ..data import Population, populations
from .. import simulation


def plot_predictions(population: Population) -> None:
    def percentage(value):
        return 100 * value / population.population

    states = list(simulation.simulate(population))
    plt.plot([percentage(state.cases) for state in states])
    plt.plot([percentage(state.immune) for state in states])
    plt.plot([percentage(state.infections) for state in states])
    plt.plot([percentage(state.recoveries) for state in states])
    plt.show()


@main.command()
def plot():
    for population in populations:
        plot_predictions(population)
