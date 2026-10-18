"""Незмінна модель прокату автомобілів (варіант 7) та базового домену замовлень."""

from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from enum import Enum
from types import MappingProxyType
from typing import NamedTuple


class Status(Enum):
    """Статус оренди."""

    BOOKED = "booked"
    ACTIVE = "active"
    RETURNED = "returned"
    CANCELLED = "cancelled"


class Option(NamedTuple):
    """Додаткова опція оренди з ціною за добу."""

    name: str
    daily_price: float


class Item(NamedTuple):
    """Позиція замовлення з базового домену."""

    sku: str
    price: float
    qty: int


def make_meta(**kwargs: str) -> Mapping[str, str]:
    """Створює тільки-читання мапу з копії переданих даних."""
    return MappingProxyType(dict(kwargs))


@dataclass(frozen=True, slots=True)
class Car:
    """Автомобіль: незмінна сутність; meta не бере участі в хешуванні."""

    plate: str
    model: str
    car_class: str
    daily_rate: float
    features: frozenset[str] = frozenset()
    meta: Mapping[str, str] = field(default_factory=make_meta, hash=False)


@dataclass(frozen=True, slots=True)
class Rental:
    """Оренда: опції у frozenset, історія статусів у tuple, meta лише для читання."""

    id: int
    car: Car
    customer: str
    days: int
    status: Status
    options: frozenset[Option] = frozenset()
    history: tuple[Status, ...] = ()
    meta: Mapping[str, str] = field(default_factory=make_meta, hash=False)


@dataclass(frozen=True, slots=True)
class Order:
    """Замовлення з базового завдання: tuple, frozenset і read-only meta."""

    id: int
    paid: bool
    items: tuple[Item, ...]
    tags: frozenset[str]
    meta: Mapping[str, str] = field(default_factory=make_meta, hash=False)

    def subtotal(self) -> float:
        """Сума позицій без знижок."""
        return sum(i.price * i.qty for i in self.items)

    def add_tag(self, tag: str) -> "Order":
        """Повертає нове замовлення з доданим тегом."""
        return replace(self, tags=self.tags | frozenset({tag}))

    def with_item(self, item: Item) -> "Order":
        """Повертає нове замовлення з доданою позицією."""
        return replace(self, items=self.items + (item,))
