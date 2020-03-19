import click

from . import simple


@click.group()
def main():
    """COVID-19 analysis"""


@main.command()
def rates():
    simple.print_rates()


@main.command()
@click.option("--geometric-mean/--no-geometric-mean", default=True)
@click.option("--exponential", is_flag=True)
def prediction(geometric_mean, exponential):
    simple.print_predictions(geometric_mean, exponential)


@main.command()
@click.option("--geometric-mean/--no-geometric-mean", default=True)
@click.option("--exponential", is_flag=True)
def saturation(geometric_mean, exponential):
    simple.print_saturation_dates(geometric_mean, exponential)
