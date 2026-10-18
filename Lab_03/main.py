"""Демонстрація pure-оновлень незмінної моделі прокату автомобілів."""

from dataclasses import FrozenInstanceError

from core import (
    add_option,
    cached_rental_total,
    change_status,
    extend_rental,
    long_rental_discount,
    total_with_discount,
    update_meta,
)
from model import Car, Option, Rental, Status, make_meta


def build_demo_rental() -> Rental:
    """Створює початкову оренду для демонстрації."""
    car = Car("AA1234BB", "Skoda Octavia", "comfort", 50.0, frozenset({"ac"}))
    return Rental(
        id=1,
        car=car,
        customer="Ivan",
        days=3,
        status=Status.BOOKED,
        history=(Status.BOOKED,),
        meta=make_meta(source="web"),
    )


def main() -> None:
    """Будує ланцюжок pure-оновлень і показує, що оригінал не змінився."""
    original = build_demo_rental()
    updated = update_meta(
        change_status(
            extend_rental(add_option(original, Option("child_seat", 5.0)), 5),
            Status.ACTIVE,
        ),
        note="vip",
    )
    print(f"original: days={original.days} status={original.status.value}")
    print(f"  options={sorted(original.options)} history={original.history}")
    print(f"updated:  days={updated.days} status={updated.status.value}")
    print(f"  options={sorted(updated.options)} history={updated.history}")
    print(f"same object: {original is updated}, equal: {original == updated}")
    print(f"total with discount: {total_with_discount(updated, long_rental_discount)}")
    cached_rental_total(updated)
    cached_rental_total(updated)
    print(f"cache: {cached_rental_total.cache_info()}")
    try:
        original.days = 10  # type: ignore[misc]
    except FrozenInstanceError as error:
        print(f"frozen: {type(error).__name__}")
    try:
        original.meta["source"] = "x"  # type: ignore[index]
    except TypeError as error:
        print(f"meta read-only: {error}")


if __name__ == "__main__":
    main()
