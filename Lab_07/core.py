"""Конвеєри на functools.partial/reduce та operator (варіант 7: бронювання)."""

from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from functools import partial, reduce
from itertools import islice
from operator import itemgetter, methodcaller
from typing import Any

from loaders import load_bookings, load_users
from models import Booking

Record = dict[str, Any]
Criteria = Sequence[tuple[str, bool]]

strip = methodcaller("strip")
lower = methodcaller("lower")
title = methodcaller("title")

get_guest = itemgetter("guest")
get_nights = itemgetter("nights")
get_room = itemgetter("room_type")
get_price = itemgetter("price")
get_status = itemgetter("status")


def pipeline(value: Any, *funcs: Callable[[Any], Any]) -> Any:
    """Пропускає значення послідовно через функції (згортка reduce)."""
    return reduce(lambda acc, f: f(acc), funcs, value)


def mapf(fn: Callable[[Any], Any]) -> Callable[[Iterable[Any]], Iterator[Any]]:
    """Часткове застосування map: mapf(fn)(iterable)."""
    return partial(map, fn)


def filt(pred: Callable[[Any], bool]) -> Callable[[Iterable[Any]], Iterator[Any]]:
    """Часткове застосування filter: filt(pred)(iterable)."""
    return partial(filter, pred)


def as_list(items: Iterable[Any]) -> list[Any]:
    """Матеріалізує ітерований об'єкт у список."""
    return list(items)


def take_n(n: int, items: Iterable[Any]) -> list[Any]:
    """Перші n елементів; від'ємне n відхиляється."""
    if n < 0:
        raise ValueError("n must be non-negative")
    return list(islice(items, n))


def multisort(rows: Iterable[Record], criteria: Criteria) -> list[Record]:
    """Багатокритеріальне сортування стабільними проходами (reduce по критеріях)."""
    return reduce(
        lambda acc, criterion: sorted(
            acc, key=itemgetter(criterion[0]), reverse=criterion[1]
        ),
        reversed(criteria),
        list(rows),
    )


def has_value(key: str, expected: Any, record: Record) -> bool:
    """Чи дорівнює поле запису очікуваному значенню."""
    return bool(itemgetter(key)(record) == expected)


def at_least(key: str, minimum: float, record: Record) -> bool:
    """Чи не менше поле запису за мінімум."""
    return bool(itemgetter(key)(record) >= minimum)


def normalize_booking(raw: Mapping[str, Any]) -> Record:
    """Очищує запис бронювання: пробіли, регістр і типи."""
    try:
        return {
            "guest": title(strip(str(get_guest(raw)))),
            "nights": int(get_nights(raw)),
            "room_type": lower(strip(str(get_room(raw)))),
            "price": float(get_price(raw)),
            "status": lower(strip(str(get_status(raw)))),
        }
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(f"Invalid booking record: {dict(raw)!r}") from error


def apply_tariff(multiplier: float, service_fee: float, record: Record) -> Record:
    """Додає total_price = ночі × ціна × коефіцієнт + збір (нова копія запису)."""
    total = get_nights(record) * get_price(record) * multiplier + service_fee
    return {**record, "total_price": round(total, 2)}


def to_booking(record: Record) -> Booking:
    """Перетворює оброблений запис на об'єкт Booking."""
    return Booking(
        guest=record["guest"],
        nights=record["nights"],
        room_type=record["room_type"],
        price=record["price"],
        status=record["status"],
        total_price=record["total_price"],
    )


high_season = partial(apply_tariff, 1.25, 10.0)
low_season = partial(apply_tariff, 0.9, 5.0)
confirmed = partial(has_value, "status", "confirmed")


def top_bookings(
    source: object,
    *,
    top: int = 3,
    tariff: Callable[[Record], Record] = high_season,
    min_nights: int = 1,
) -> list[Booking]:
    """Завантаження, очищення, тариф, відбір підтверджених і Top-N за вартістю."""
    result: list[Booking] = pipeline(
        load_bookings(source),
        mapf(normalize_booking),
        mapf(tariff),
        filt(confirmed),
        filt(partial(at_least, "nights", min_nights)),
        as_list,
        partial(multisort, criteria=(("total_price", True), ("guest", False))),
        partial(take_n, top),
        mapf(to_booking),
        as_list,
    )
    return result


def normalize_student(raw: Mapping[str, Any]) -> Record:
    """Очищує запис студента: пробіли, регістр імені та типи."""
    return {
        "name": title(strip(str(itemgetter("name")(raw)))),
        "age": int(itemgetter("age")(raw)),
        "score": float(itemgetter("score")(raw)),
    }


def clean_and_rank(source: object, top: int = 3) -> list[Record]:
    """Студенти: очищення, age ≥ 18, сортування за score ↓ і name ↑, Top-N."""
    result: list[Record] = pipeline(
        load_users(source),
        mapf(normalize_student),
        filt(partial(at_least, "age", 18)),
        as_list,
        partial(multisort, criteria=(("score", True), ("name", False))),
        partial(take_n, top),
    )
    return result


def sort_products(products: Iterable[Record]) -> list[Record]:
    """Товари: за category ↑, price ↓, name ↑."""
    return multisort(products, (("category", False), ("price", True), ("name", False)))
