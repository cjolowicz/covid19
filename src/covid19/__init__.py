import click

from . import simulation


@click.group()
def main():
    """COVID-19 analysis"""


@main.command()
def rates():
    simulation.print_rates()


@main.command()
def simulate():
    simulation.run()
