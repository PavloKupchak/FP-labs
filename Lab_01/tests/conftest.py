import pytest

from core import Order, Reading


@pytest.fixture
def sample_readings() -> list[Reading]:
    return [
        {"id": 1, "prev": 100.0, "curr": 250.0, "group": "household"},
        {"id": 2, "prev": 0.0, "curr": 200.0, "group": "pensioner"},
        {"id": 3, "prev": 500.0, "curr": 400.0, "group": "commercial"},
        {"id": 4, "prev": 10.0, "curr": 10.0, "group": "household"},
    ]


@pytest.fixture
def rates() -> dict[str, float]:
    return {"household": 4.0, "pensioner": 4.0, "commercial": 6.0}


@pytest.fixture
def benefit_shares() -> dict[str, float]:
    return {"pensioner": 0.5}


@pytest.fixture
def sample_orders() -> list[Order]:
    return [
        {"id": 1, "items": [{"price": 50.0, "qty": 3}], "paid": True},
        {"id": 2, "items": [{"price": 10.0, "qty": 2}], "paid": True},
        {"id": 3, "items": [{"price": 200.0, "qty": 1}], "paid": False},
        {
            "id": 4,
            "items": [{"price": 40.0, "qty": 2}, {"price": 30.0, "qty": 1}],
            "paid": True,
        },
    ]
