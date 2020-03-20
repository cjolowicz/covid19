import datetime
from pathlib import Path
import tempfile

import click
import imageio
import matplotlib.pyplot as plt

from .main import main
from .plot import plot_predictions
from .. import data, simulation


def create_image(population: data.Population, tempdir: str, days: int):
    image = str(Path(tempdir) / "{days:03}.png")
    date = population.start + datetime.timedelta(days=days)

    states = simulation.simulate(population, version=date)

    plt.xlim(
        left=population.start, right=population.start + datetime.timedelta(days=200),
    )

    plot_predictions(
        population, list(states), version=date, plots=["cases"], output=image
    )

    plt.close()

    return imageio.imread(image)


@main.command()
@click.option(
    "--population",
    "-p",
    default="Germany",
    show_default=True,
    type=click.Choice([population.name for population in data.populations]),
)
@click.option(
    "--output", "-o", metavar="FILE", default="covid19.gif", show_default=True,
)
def animate(population: str, output: str):
    _population: data.Population = data.find(population)
    start = max(simulation.PROBABILITY_WINDOW_SIZE, len(_population.cases) - 14)
    stop = len(_population.cases)

    with tempfile.TemporaryDirectory() as tempdir:
        images = [
            create_image(_population, tempdir, days) for days in range(start, stop)
        ]
        imageio.mimwrite(output, images, format="GIF", fps=1, loop=1)
