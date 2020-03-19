import matplotlib.pyplot as plt

import click

from .main import main
from ..data import Population, populations
from .. import simulation


def plot_predictions(population: Population) -> None:
    def percentage(value):
        return 100 * value / population.population

    states = list(simulation.simulate(population))
    plt.title(population.name)
    plt.xlabel("days")
    plt.ylabel("% of population")
    plt.grid(True)
    plt.plot([percentage(state.cases) for state in states], label="cases")
    plt.plot([percentage(state.immune) for state in states], label="immune")
    plt.plot([percentage(state.infections) for state in states], label="infections")
    plt.plot([percentage(state.recoveries) for state in states], label="recoveries")
    plt.legend()


@main.command()
def plot():
    for index, population in enumerate(populations):
        plt.subplot(311 + index * 2)
        plot_predictions(population)
    plt.show()
