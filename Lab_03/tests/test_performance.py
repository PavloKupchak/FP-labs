import time
from typing import Any

from core import add_option, change_status, extend_rental
from model import Option, Status
from tests.conftest import build_rental

RENTALS = 5_000


def mutable_rental() -> dict[str, Any]:
    return {
        "days": 3,
        "status": "booked",
        "options": {("child_seat", 5.0)},
        "history": ["booked"],
    }


def mutable_update(rental: dict[str, Any], i: int) -> None:
    rental["options"].add((f"opt{i % 5}", 1.0))
    rental["days"] += 1
    rental["status"] = "active"
    rental["history"].append("active")


def test_immutable_matches_mutable_result_and_timing() -> None:
    start = time.perf_counter()
    legacy = [mutable_rental() for _ in range(RENTALS)]
    for i, rental in enumerate(legacy):
        mutable_update(rental, i)
    mutable_time = time.perf_counter() - start

    start = time.perf_counter()
    modern = [build_rental() for _ in range(RENTALS)]
    modern = [
        change_status(
            extend_rental(add_option(rental, Option(f"opt{i % 5}", 1.0)), 1),
            Status.ACTIVE,
        )
        for i, rental in enumerate(modern)
    ]
    immutable_time = time.perf_counter() - start

    assert [r.days for r in modern] == [r["days"] for r in legacy]
    assert [len(r.history) for r in modern] == [len(r["history"]) for r in legacy]
    assert mutable_time > 0
    assert immutable_time > 0
    print(f"mutable={mutable_time:.4f}s immutable={immutable_time:.4f}s")
