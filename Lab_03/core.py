"""Чисті оновлення та розрахунки над незмінними моделями.

Жодна функція не змінює вхідні об'єкти: усі оновлення повертають нові копії.
"""

from collections.abc import Callable, Mapping, Sequence
from dataclasses import replace
from functools import lru_cache
from types import MappingProxyType
from typing import Any

from model import Car, Item, Option, Order, Rental, Status

DiscountFn = Callable[[int], float]

MODIFIABLE_STATUSES: frozenset[Status] = frozenset({Status.BOOKED, Status.ACTIVE})


def add_option(rental: Rental, option: Option) -> Rental:
    """Нова оренда з додатковою опцією (повторне додавання нічого не змінює)."""
    return replace(rental, options=rental.options | frozenset({option}))


def remove_option(rental: Rental, name: str) -> Rental:
    """Нова оренда без опції із заданою назвою."""
    kept = frozenset(o for o in rental.options if o.name != name)
    return replace(rental, options=kept)


def extend_rental(rental: Rental, extra_days: int) -> Rental:
    """Нова оренда з більшою кількістю днів; діє лише для бронювання й активної."""
    if extra_days <= 0:
        raise ValueError("extra_days must be positive")
    if rental.status not in MODIFIABLE_STATUSES:
        raise ValueError("rental can not be extended in this status")
    return replace(rental, days=rental.days + extra_days)


def change_status(rental: Rental, status: Status) -> Rental:
    """Нова оренда з іншим статусом; попередній статус додається в історію."""
    return replace(rental, status=status, history=rental.history + (status,))


def update_meta(rental: Rental, **changes: str) -> Rental:
    """Нова оренда з оновленими метаданими (копія мапи, оригінал не змінюється)."""
    return replace(rental, meta=MappingProxyType({**rental.meta, **changes}))


def add_feature(car: Car, feature: str) -> Car:
    """Новий автомобіль з додатковою характеристикою."""
    return replace(car, features=car.features | frozenset({feature}))


def rental_total(rental: Rental) -> float:
    """Вартість оренди: (ставка авто + ціна опцій за добу) × кількість днів."""
    daily = rental.car.daily_rate + sum(o.daily_price for o in rental.options)
    return daily * rental.days


def long_rental_discount(days: int) -> float:
    """Політика знижки: 10% за оренду від семи днів."""
    return 0.1 if days >= 7 else 0.0


def total_with_discount(rental: Rental, discount: DiscountFn) -> float:
    """Вартість оренди після знижки, що залежить від тривалості."""
    return rental_total(rental) * (1 - discount(rental.days))


cached_rental_total = lru_cache(maxsize=None)(rental_total)


def freeze(obj: Any) -> Any:
    """Глибоко заморожує вкладені структури у tuple, frozenset і read-only мапи."""
    if isinstance(obj, Mapping):
        return MappingProxyType({k: freeze(v) for k, v in obj.items()})
    if isinstance(obj, set | frozenset):
        return frozenset(freeze(x) for x in obj)
    if isinstance(obj, list | tuple):
        return tuple(freeze(x) for x in obj)
    return obj


def add_vip_tag(order: Order) -> Order:
    """Нове замовлення з тегом vip."""
    return order.add_tag("vip")


def add_item(order: Order, sku: str, price: float, qty: int) -> Order:
    """Нове замовлення з додатковою позицією."""
    return order.with_item(Item(sku, price, qty))


def top_expensive_items(items: Sequence[Item], n: int = 3) -> tuple[Item, ...]:
    """Кортеж n найдорожчих позицій за сумою рядка."""
    ranked = sorted(items, key=lambda i: i.price * i.qty, reverse=True)
    return tuple(ranked[:n])


def source(meta: Mapping[str, str]) -> str:
    """Джерело замовлення з метаданих."""
    return meta.get("source", "unknown")
