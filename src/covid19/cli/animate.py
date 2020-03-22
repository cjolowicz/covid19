import datetime
from pathlib import Path
import tempfile

import click
import imageio
import matplotlib.pyplot as plt

from .main import main
from .plot import plot_predictions
from .. import populations, simulation


def create_image(population: populations.Population, tempdir: str, days: int):
    image = str(Path(tempdir) / "{days:03}.png")
    date = population.start + datetime.timedelta(days=days)
    end = population.start + datetime.timedelta(days=120)

    states = list(simulation.simulate(population, version=date, end=end))
    if states[-1].probability == 0:
        return

    kwargs = dict(version=date, plots=["cases"], output=image, legend=False)

    plt.xlim(left=population.start, right=end)
    line = plt.axvline(x=date, color="tab:gray")
    plot_predictions(population, states, **kwargs)

    yield imageio.imread(image)

    line.remove()
    plot_predictions(population, states, color="moccasin", **kwargs)


def create_images(population: populations.Population, tempdir: str):
    start = simulation.PROBABILITY_WINDOW_SIZE + 3
    stop = len(population.cases)
    for days in range(start, stop):
        yield from create_image(population, tempdir, days)


@main.command()
@click.option(
    "--population",
    "-p",
    default="Germany",
    show_default=True,
    type=click.Choice(populations.populations, case_sensitive=False,),
)
@click.option(
    "--output", "-o", metavar="FILE", default="covid19.gif", show_default=True,
)
def animate(population: str, output: str):
    _population = populations.load(population)

    with tempfile.TemporaryDirectory() as tempdir:
        images = list(create_images(_population, tempdir))
        images += images[-1:] * 5
        imageio.mimwrite(output, images, format="GIF", fps=2)
