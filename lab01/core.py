from collections.abc import Callable, Iterable, Mapping
from typing import TypedDict, TypeVar

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


class Reading(TypedDict, total=False):
    id: int
    prev: float
    curr: float
    group: str
    consumption: float
    amount: float


class Result(TypedDict):
    count: int
    consumption: float
    amount: float
    bills: list[Reading]


AcceptFn = Callable[[float], bool]
TariffFn = Callable[[str, float], float]
BenefitFn = Callable[[str, float], float]
NowFn = Callable[[], float]
Processor = Callable[[Iterable[Reading]], Result]


def compose(f: Callable[[B], C], g: Callable[[A], B]) -> Callable[[A], C]:
    return lambda x: f(g(x))


def make_multiplier(k: int) -> Callable[[int], int]:
    return lambda x: x * k


def is_valid_reading(reading: Reading) -> bool:
    return reading["curr"] >= reading["prev"]


def consumption_of(reading: Reading) -> float:
    return reading["curr"] - reading["prev"]


def with_bill(reading: Reading, consumption: float, amount: float) -> Reading:
    return {**reading, "consumption": consumption, "amount": amount}


def stamp_amount(amount: float, now: NowFn) -> tuple[float, float]:
    return amount, now()


def make_min_consumption_filter(min_consumption: float) -> AcceptFn:
    return lambda consumption: consumption >= min_consumption


def make_flat_tariff(rates: Mapping[str, float]) -> TariffFn:
    return lambda group, consumption: consumption * rates[group]


def make_group_benefit(shares: Mapping[str, float]) -> BenefitFn:
    return lambda group, amount: amount * (1 - shares.get(group, 0.0))


def make_processor(
    *,
    accept: AcceptFn,
    tariff: TariffFn,
    benefit: BenefitFn,
) -> Processor:
    def price(group: str, consumption: float) -> float:
        return benefit(group, tariff(group, consumption))

    def process(readings: Iterable[Reading]) -> Result:
        measured = [(r, consumption_of(r)) for r in readings if is_valid_reading(r)]
        bills = [
            with_bill(r, c, price(r["group"], c)) for r, c in measured if accept(c)
        ]
        return {
            "count": len(bills),
            "consumption": sum(b["consumption"] for b in bills),
            "amount": sum(b["amount"] for b in bills),
            "bills": bills,
        }

    return process


def process_readings_pure(
    readings: Iterable[Reading],
    *,
    rates: Mapping[str, float],
    benefit_shares: Mapping[str, float],
    min_consumption: float,
) -> Result:
    processor = make_processor(
        accept=make_min_consumption_filter(min_consumption),
        tariff=make_flat_tariff(rates),
        benefit=make_group_benefit(benefit_shares),
    )
    return processor(readings)
