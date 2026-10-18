"""Мутабельна модель оренди «до» переходу на незмінні структури (для порівняння)."""

from typing import Any


def mutable_rental() -> dict[str, Any]:
    """Оренда як звичайний словник: множина опцій і список історії змінюються на місці."""
    return {
        "days": 3,
        "status": "booked",
        "options": {("child_seat", 5.0)},
        "history": ["booked"],
    }


def mutable_update(rental: dict[str, Any], i: int) -> None:
    """Змінює оренду на місці: додає опцію, день, статус та запис в історію."""
    rental["options"].add((f"opt{i % 5}", 1.0))
    rental["days"] += 1
    rental["status"] = "active"
    rental["history"].append("active")
