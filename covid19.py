from dataclasses import dataclass
import datetime
from itertools import count


last_updated = datetime.date.fromisoformat("2020-03-14")


def to_ratios(cases):
    return [(y / x) for x, y in zip(cases, cases[1:])]


class Berlin:
    population = 3_700_000
    cases = [1, 3, 6, 9, 15, 24, 28, 40, 48, 90, 137, 174, 216]
    ratios = to_ratios(cases)


class Germany:
    population = 82_900_000
    cases = [16, 18, 21, 26, 53, 66, 117, 150, 188, 242, 354, 534, 684, 847, 1112, 1460, 1884, 2369, 3062, 3795]
    ratios = to_ratios(cases)


@dataclass
class Prediction:
    days: int
    date: datetime.date
    cases: int
    percent: float

    @classmethod
    def _predict(cls, days, cases, rate, population):
        date = last_updated + datetime.timedelta(days=days)
        cases = int(cases * rate ** days)
        percent = min(100, 100 * cases / population)
        return cls(days, date, cases, percent)

    @classmethod
    def predict(cls, days, klass):
        return cls._predict(days, klass.cases[-1], klass.ratios[-1], klass.population)


def header(message):
    print()
    print(message)
    print("=" * len(message))
    print()


def predict(klass):
    header(f"{klass.__name__}, growth rate = {klass.ratios[-1]:.2f}")

    for days in count():
        prediction = Prediction.predict(days, klass)
        print(f"{prediction.days:3}  {prediction.date:%b %d}  {prediction.percent:6.2f}%  {prediction.cases:8}")

        if prediction.percent >= 100:
            break


def predict_saturation(klass, rate):
    for days in count():
        prediction = Prediction._predict(days, klass.cases[-1], rate, klass.population)
        if prediction.percent >= 100:
            return prediction


def by_growth_rate(klass):
    header(f"{klass.__name__}")

    for rate in count(klass.ratios[-1], -0.01):
        if rate < 1.01:
            break
        prediction = predict_saturation(klass, rate)
        print(f"{rate:.2f}  |  {prediction.days:4} days  |  {prediction.date:%b %d %Y}")


if __name__ == "__main__":
    by_growth_rate(Berlin)
    by_growth_rate(Germany)
