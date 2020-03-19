from dataclasses import dataclass
import datetime
from itertools import count
import statistics

from . import data


eta = 0.0001


@dataclass
class Options:
    exponential: bool = False


options = Options()


def to_rates(cases):
    return [(y / x) for x, y in zip(cases, cases[1:])]


def growth_rate(population):
    rates = to_rates(population.cases)
    return (
        statistics.geometric_mean(rates[-5:]) if options.geometric_mean else rates[-1]
    )


def predict_once(cases, rate, population):
    return int(cases * (1 + (rate - 1) * (1 - (cases / population))))


def predict(days, cases, rate, population):
    if options.exponential:
        return int(cases * rate ** days)
    for _ in range(days):
        cases = predict_once(cases, rate, population)
    return cases


@dataclass
class Prediction:
    days: int
    date: datetime.date
    cases: int
    percent: float

    @classmethod
    def predict(cls, days, cases, rate, population):
        date = data.last_updated + datetime.timedelta(days=days)
        cases = predict(days, cases, rate, population)
        percent = min(100, 100 * cases / population)
        return cls(days, date, cases, percent)

    @classmethod
    def predict_class(cls, days, klass):
        return cls.predict(
            days, klass.cases[-1], growth_rate(klass), klass.population
        )


def is_saturated(prediction, previous):
    if prediction.percent >= 100:
        return True

    if previous is not None:
        return prediction.cases / previous.cases < 1 + eta

    return False


def predict_saturation(klass, rate):
    prediction = None

    for days in count():
        previous = prediction
        prediction = Prediction.predict(days, klass.cases[-1], rate, klass.population)

        if is_saturated(prediction, previous):
            return prediction


def print_heading(heading):
    print()
    print(heading)
    print("=" * len(heading))
    print()


def print_predictions_by_day(klass):
    print_heading(f"{klass.__name__}, growth rate = {growth_rate(klass):.2f}")
    prediction = None

    for days in count():
        previous = prediction
        prediction = Prediction.predict_class(days, klass)
        print(
            f"{prediction.days:3}  {prediction.date:%b %d}  {prediction.percent:6.2f}%  {prediction.cases:8}"
        )

        if is_saturated(prediction, previous):
            break


def print_saturation_date_for_growth_rates(klass):
    print_heading(f"{klass.__name__}")

    for rate in count(growth_rate(klass), -0.01):
        if rate < 1.01:
            break
        prediction = predict_saturation(klass, rate)
        print(
            f"{rate:.2f}  |  {prediction.days:4} days  |  {prediction.date:%b %d %Y}  {prediction.percent:6.2f}%  {prediction.cases:8}"
        )
