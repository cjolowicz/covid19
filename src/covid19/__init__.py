import click

from . import simulation


@click.group()
def main():
    """COVID-19 analysis"""


@main.command()
@click.option("--recovery/--no-recovery")
def rates(recovery: bool):
    simulation.print_rates(recovery)


@main.command()
def simulate():
    simulation.run()
