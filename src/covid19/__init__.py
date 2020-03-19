import click

from . import data, simple


@click.group()
def main():
    """COVID-19 analysis"""


@main.command()
def rates():
    for population in data.populations:
        simple.print_heading(population.__name__)
        for rate in simple.to_rates(population.cases):
            print(f"{rate:.2f}", end=" ")
        print()


@main.command()
@click.option("--geometric-mean/--no-geometric-mean", default=True)
@click.option("--exponential", is_flag=True)
def prediction(geometric_mean, exponential):
    simple.options.geometric_mean = geometric_mean
    simple.options.exponential = exponential
    for population in data.populations:
        simple.print_predictions_by_day(population)


@main.command()
@click.option("--geometric-mean/--no-geometric-mean", default=True)
@click.option("--exponential", is_flag=True)
def saturation(geometric_mean, exponential):
    simple.options.geometric_mean = geometric_mean
    simple.options.exponential = exponential
    for population in data.populations:
        simple.print_saturation_date_for_growth_rates(population)
