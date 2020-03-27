"""
Data from daily situation reports of the Robert Koch Institute (RKI).

https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Situationsberichte/Gesamt.html

via: https://de.wikipedia.org/wiki/COVID-19-Pandemie_in_Deutschland
"""

import datetime

from ..populations import Population


populations = [
    Population(
        name="Berlin",
        population=3_700_000,
        start=datetime.date.fromisoformat("2020-03-02"),
        cases=[
            1,
            3,
            6,
            13,
            19,
            28,
            40,
            48,
            48,
            90,
            137,
            174,
            216,
            265,
            300,
            345,
            391,
            573,
            731,
            866,
            1024,
            1077,
            1220,
            1428,
            1656,
            1955,
        ],
    ),
    Population(
        name="Germany",
        population=82_900_000,
        start=datetime.date.fromisoformat("2020-02-24"),
        cases=[
            16,
            18,
            21,
            26,
            53,
            66,
            117,
            150,
            188,
            240,
            400,
            639,
            795,
            902,
            1139,
            1296,
            1567,
            2369,
            3062,
            3795,
            4838,
            6012,
            7156,
            8198,
            10999,
            13957,
            16662,
            18610,
            22672,
            27436,
            31554,
            36508,
            42288,
        ],
    ),
]


def load(name: str) -> Population:
    for population in populations:
        if name.lower() == population.name.lower():
            return population

    raise ValueError(f"unknown population {name}")
