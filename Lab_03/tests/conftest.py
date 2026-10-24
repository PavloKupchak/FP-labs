import pytest

from model import Car, Item, Option, Order, Rental, Status, make_meta


def build_car() -> Car:
    return Car(
        plate="AA1234BB",
        model="Skoda Octavia",
        car_class="comfort",
        daily_rate=50.0,
        features=frozenset({"ac", "gps"}),
        meta=make_meta(color="blue"),
    )


def build_rental() -> Rental:
    return Rental(
        id=1,
        car=build_car(),
        customer="Ivan",
        days=3,
        status=Status.BOOKED,
        options=frozenset({Option("child_seat", 5.0)}),
        history=(Status.BOOKED,),
        meta=make_meta(source="web"),
    )


def build_order() -> Order:
    return Order(
        id=10,
        paid=True,
        items=(Item("A1", 50.0, 2), Item("B2", 20.0, 1)),
        tags=frozenset({"delhi", "priority"}),
        meta=make_meta(source="fb_ads", campaign="summer"),
    )


@pytest.fixture
def sample_car() -> Car:
    return build_car()


@pytest.fixture
def sample_rental() -> Rental:
    return build_rental()


@pytest.fixture
def sample_order() -> Order:
    return build_order()
