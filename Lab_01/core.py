"""Чисте ядро обліку електроенергії (варіант 7) та базових функцій лабораторної.

Усі функції модуля чисті: не виконують I/O, не використовують глобальний стан
і не змінюють вхідні дані, а повертають нові об'єкти.
Політики фільтрації, тарифу та пільги передаються як ``Callable``.
"""

from collections.abc import Callable, Iterable, Mapping
from typing import TypedDict, TypeVar

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


class Reading(TypedDict, total=False):
    """Показник лічильника; consumption і amount з'являються в результаті."""

    id: int
    prev: float
    curr: float
    group: str
    consumption: float
    amount: float


class Result(TypedDict):
    """Результат обробки показників: нові записи та підсумки."""

    count: int
    consumption: float
    amount: float
    bills: list[Reading]


AcceptFn = Callable[[float], bool]
TariffFn = Callable[[str, float], float]
BenefitFn = Callable[[str, float], float]
NowFn = Callable[[], float]
ReadingProcessor = Callable[[Iterable[Reading]], Result]


def compose(f: Callable[[B], C], g: Callable[[A], B]) -> Callable[[A], C]:
    """Повертає композицію функцій: x -> f(g(x))."""
    return lambda x: f(g(x))


def identity(x: A) -> A:
    """Повертає аргумент без змін (нейтральна політика)."""
    return x


def make_multiplier(k: int) -> Callable[[int], int]:
    """Фабрика функцій, що множать число на k."""
    return lambda x: x * k


def is_valid_reading(reading: Reading) -> bool:
    """Показник коректний, якщо поточне значення не менше за попереднє."""
    return reading["curr"] >= reading["prev"]


def consumption_of(reading: Reading) -> float:
    """Спожита енергія: різниця поточного і попереднього показників."""
    return reading["curr"] - reading["prev"]


def with_bill(reading: Reading, consumption: float, amount: float) -> Reading:
    """Повертає НОВИЙ запис із споживанням і сумою (вхідний не змінюється)."""
    return {**reading, "consumption": consumption, "amount": amount}


def stamp_amount(amount: float, now: NowFn) -> tuple[float, float]:
    """Додає до суми час розрахунку; джерело часу передається ззовні."""
    return amount, now()


def make_min_consumption_filter(min_consumption: float) -> AcceptFn:
    """Фабрика фільтра: споживання не менше за мінімальне."""
    return lambda consumption: consumption >= min_consumption


def make_flat_tariff(rates: Mapping[str, float]) -> TariffFn:
    """Фабрика тарифу: ціна за кВт·год залежить від тарифної групи."""
    frozen = dict(rates)
    return lambda group, consumption: consumption * frozen[group]


def make_group_benefit(shares: Mapping[str, float]) -> BenefitFn:
    """Фабрика пільги: частка знижки залежить від тарифної групи."""
    frozen = dict(shares)
    return lambda group, amount: amount * (1 - frozen.get(group, 0.0))


def make_reading_processor(
    *,
    accept: AcceptFn,
    tariff: TariffFn,
    benefit: BenefitFn,
) -> ReadingProcessor:
    """Функція вищого порядку: збирає обробник показників із політик."""

    def price(group: str, consumption: float) -> float:
        """Сума до оплати: тариф, потім пільга."""
        return benefit(group, tariff(group, consumption))

    def process(readings: Iterable[Reading]) -> Result:
        """Повертає новий результат, не змінюючи вхідні записи."""
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
    """Розраховує показники зі стандартними політиками; усі параметри явні."""
    processor = make_reading_processor(
        accept=make_min_consumption_filter(min_consumption),
        tariff=make_flat_tariff(rates),
        benefit=make_group_benefit(benefit_shares),
    )
    return processor(readings)


class Item(TypedDict):
    """Позиція замовлення з базового завдання."""

    price: float
    qty: int


class Order(TypedDict, total=False):
    """Замовлення з базового завдання; поле total з'являється в результаті."""

    id: int
    items: list[Item]
    paid: bool
    total: float


FilterFn = Callable[[float], bool]
DiscountFn = Callable[[float], float]
TaxFn = Callable[[float], float]
OrdersProcessor = Callable[[Iterable[Order]], dict[str, object]]


def order_subtotal(order: Order) -> float:
    """Сума замовлення без знижки і податку."""
    return sum(it["price"] * it["qty"] for it in order["items"])


def with_total(order: Order, total: float) -> Order:
    """Повертає НОВЕ замовлення з полем total (вхідне не змінюється)."""
    return {**order, "total": total}


def make_processor(
    *,
    accept: FilterFn,
    apply_discount: DiscountFn,
    apply_tax: TaxFn,
) -> OrdersProcessor:
    """Функція вищого порядку для замовлень: політики передаються як Callable."""

    def process(orders: Iterable[Order]) -> dict[str, object]:
        """Відбирає оплачені замовлення і рахує нові записи з total."""
        paid = [o for o in orders if o["paid"]]
        accepted = [o for o in paid if accept(order_subtotal(o))]
        qualified = [
            with_total(o, apply_tax(apply_discount(order_subtotal(o))))
            for o in accepted
        ]
        revenue = sum(o["total"] for o in qualified)
        return {"count": len(qualified), "revenue": revenue, "orders": qualified}

    return process


def process_orders_pure(
    orders: Iterable[Order],
    *,
    min_total: float,
    discount: float,
    tax_rate: float,
) -> dict[str, object]:
    """Чиста версія стартового process_orders: усі параметри передаються явно."""
    processor = make_processor(
        accept=lambda s: s >= min_total,
        apply_discount=lambda s: s * (1 - discount),
        apply_tax=lambda s: s * (1 + tax_rate),
    )
    return processor(orders)
