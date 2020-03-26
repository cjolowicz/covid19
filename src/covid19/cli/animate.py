import datetime
from pathlib import Path
import tempfile

import click
import imageio
import matplotlib.pyplot as plt

from . import options
from .main import main
from .plot import plot_predictions
from .. import data, simulation
from ..populations import Population


def simulate(population: Population, start: int, stop: int, end: datetime.date):
    for days in range(start, stop):
        date = population.start + datetime.timedelta(days=days)
        states = list(simulation.simulate(population, version=date, end=end))
        if states[-1].probability != 0:
            yield date, states


def create_image(population: Population, tempdir: str, date, states, yscale: str):
    image = str(Path(tempdir) / "{date:%Y%m%d}.png")
    kwargs = dict(
        version=date, plots=["cases"], output=image, legend=False, yscale=yscale
    )

    line = plt.axvline(x=date, color="tab:gray")
    plot_predictions(population, states, **kwargs)

    yield imageio.imread(image)

    line.remove()
    plot_predictions(population, states, color="moccasin", **kwargs)


def create_images(population: Population, tempdir: str, yscale: str):
    start = simulation.PROBABILITY_WINDOW_SIZE + 3
    stop = len(population.cases)
    end = population.start + datetime.timedelta(days=182)
    simulations = list(simulate(population, start, stop, end))
    plt.xlim(left=simulations[0][0], right=end)
    for date, states in simulations:
        yield from create_image(population, tempdir, date, states, yscale)


@main.command()
@options.population
@options.data_source
@click.option(
    "--output", "-o", metavar="FILE", default="covid19.gif", show_default=True
)
@options.yscale
def animate(population: str, data_source: str, output: str, yscale: str):
    _population = data.load(population, source=data_source)

    with tempfile.TemporaryDirectory() as tempdir:
        images = list(create_images(_population, tempdir, yscale))
        images += images[-1:] * 5
        imageio.mimwrite(output, images, format="GIF", fps=2)
