import io
import operator
import runpy
from functools import partial, reduce
from operator import attrgetter, itemgetter, methodcaller
from pathlib import Path
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st

from core import (
    Record,
    apply_tariff,
    as_list,
    at_least,
    clean_and_rank,
    confirmed,
    filt,
    has_value,
    high_season,
    low_season,
    mapf,
    multisort,
    normalize_booking,
    normalize_student,
    pipeline,
    sort_products,
    take_n,
    to_booking,
    top_bookings,
)
from loaders import load_bookings, load_users, parse_records
from main import DATA_DIR, main
from models import Booking, Box

BOOKINGS_JSON = (
    '[{"guest": " alice smith ", "nights": 3, "room_type": " Deluxe ", '
    '"price": 120.0, "status": "Confirmed"},'
    ' {"guest": "bob stone", "nights": 1, "room_type": "standard", '
    '"price": 70.0, "status": "cancelled"},'
    ' {"guest": "Carol Day", "nights": 5, "room_type": "Suite", '
    '"price": 200.0, "status": " confirmed"},'
    ' {"guest": "Eva Moon", "nights": 4, "room_type": "deluxe", '
    '"price": 110.0, "status": "CONFIRMED"}]'
)

BOOKINGS_CSV = (
    "guest,nights,room_type,price,status\n"
    " alice smith ,3, Deluxe ,120.0,Confirmed\n"
    "bob stone,1,standard,70.0,cancelled\n"
    "Carol Day,5,Suite,200.0, confirmed\n"
    "Eva Moon,4,deluxe,110.0,CONFIRMED\n"
)

STUDENTS_JSON = (
    '[{"name": "  ALICE  ", "age": "19", "score": "8.5"},'
    ' {"name": "bob", "age": "17", "score": "9.1"},'
    ' {"name": "Carol", "age": "21", "score": "7.0"},'
    ' {"name": "denis", "age": "20", "score": "9.3"},'
    ' {"name": "adam", "age": "22", "score": "8.5"}]'
)


@pytest.fixture
def bookings_records() -> list[dict[str, Any]]:
    return [
        {
            "guest": " alice smith ",
            "nights": 3,
            "room_type": " Deluxe ",
            "price": 120.0,
            "status": "Confirmed",
        },
        {
            "guest": "bob stone",
            "nights": 1,
            "room_type": "standard",
            "price": 70.0,
            "status": "cancelled",
        },
        {
            "guest": "Carol Day",
            "nights": 5,
            "room_type": "Suite",
            "price": 200.0,
            "status": " confirmed",
        },
    ]


# ---------- reduce / pipeline ----------


def test_reduce_with_initial_value() -> None:
    assert reduce(operator.mul, [], 1) == 1
    assert reduce(operator.add, [1, 2, 3], 0) == 6
    assert reduce(operator.mul, range(1, 6), 1) == 120


def test_pipeline_applies_functions_in_order() -> None:
    def inc(x: int) -> int:
        return x + 1

    def dbl(x: int) -> int:
        return x * 2

    assert pipeline(3, inc, dbl, inc) == 9
    assert pipeline(3) == 3


def test_pipeline_with_partial() -> None:
    square = partial(pow, exp=2)
    cube = partial(pow, exp=3)
    assert square(5) == 25
    assert cube(2) == 8
    assert pipeline(2, square, cube) == 64


def test_mapf_and_filt_are_lazy_partials() -> None:
    doubled = mapf(lambda x: x * 2)([1, 2, 3])
    assert iter(doubled) is doubled
    assert as_list(doubled) == [2, 4, 6]
    assert as_list(filt(lambda x: x > 1)([1, 2, 3])) == [2, 3]


# ---------- operator ----------


def test_itemgetter_methodcaller_attrgetter() -> None:
    row = {"name": "  ALICE  ", "age": "19"}
    assert itemgetter("name")(row) == "  ALICE  "
    assert itemgetter("name", "age")(row) == ("  ALICE  ", "19")
    assert methodcaller("title")(methodcaller("strip")("  aLiCe ")) == "Alice"
    assert methodcaller("split", ",")("a,b") == ["a", "b"]
    boxes = [Box(1, 2, 3), Box(3, 3, 3)]
    assert [b.w for b in sorted(boxes, key=attrgetter("w"), reverse=True)] == [3, 1]


def test_itemgetter_multi_key_sorting() -> None:
    rows = [{"a": 1, "b": 2}, {"a": 1, "b": 1}, {"a": 0, "b": 9}]
    assert sorted(rows, key=itemgetter("a", "b")) == [
        {"a": 0, "b": 9},
        {"a": 1, "b": 1},
        {"a": 1, "b": 2},
    ]


# ---------- multisort / take_n ----------


def test_multisort_mixed_directions_is_stable() -> None:
    rows: list[Record] = [
        {"score": 8.5, "name": "Alice"},
        {"score": 9.3, "name": "Denis"},
        {"score": 8.5, "name": "Adam"},
    ]
    result = multisort(rows, (("score", True), ("name", False)))
    assert [r["name"] for r in result] == ["Denis", "Adam", "Alice"]
    assert [r["name"] for r in rows] == ["Alice", "Denis", "Adam"]


def test_multisort_empty_and_no_criteria() -> None:
    assert multisort([], (("a", True),)) == []
    rows: list[Record] = [{"a": 2}, {"a": 1}]
    assert multisort(rows, ()) == rows


@given(
    st.lists(
        st.fixed_dictionaries(
            {"x": st.integers(0, 3), "y": st.integers(0, 3), "z": st.integers(0, 3)}
        ),
        max_size=25,
    )
)
def test_multisort_matches_composite_key(rows: list[Record]) -> None:
    expected = sorted(rows, key=lambda r: (r["x"], -r["y"], r["z"]))
    result = multisort(rows, (("x", False), ("y", True), ("z", False)))
    assert [(r["x"], r["y"], r["z"]) for r in result] == [
        (r["x"], r["y"], r["z"]) for r in expected
    ]


def test_take_n_edge_cases() -> None:
    assert take_n(0, [1, 2]) == []
    assert take_n(5, [1, 2]) == [1, 2]
    assert take_n(2, iter(range(100))) == [0, 1]
    with pytest.raises(ValueError):
        take_n(-1, [1])


def test_sort_products_by_category_price_name() -> None:
    products: list[Record] = [
        {"category": "b", "price": 5, "name": "x"},
        {"category": "a", "price": 5, "name": "y"},
        {"category": "a", "price": 9, "name": "z"},
        {"category": "a", "price": 5, "name": "c"},
    ]
    result = sort_products(products)
    assert [(p["category"], p["price"], p["name"]) for p in result] == [
        ("a", 9, "z"),
        ("a", 5, "c"),
        ("a", 5, "y"),
        ("b", 5, "x"),
    ]


# ---------- partial: тарифи та фільтри ----------


def test_apply_tariff_via_partial() -> None:
    record: Record = {"nights": 3, "price": 100.0}
    assert high_season(record)["total_price"] == 385.0
    assert low_season(record)["total_price"] == 275.0
    assert "total_price" not in record
    custom = partial(apply_tariff, 1.0, 0.0)
    assert custom(record)["total_price"] == 300.0


def test_filters_via_partial() -> None:
    assert confirmed({"status": "confirmed"}) is True
    assert confirmed({"status": "pending"}) is False
    assert has_value("a", 1, {"a": 1}) is True
    assert partial(at_least, "nights", 3)({"nights": 3}) is True
    assert partial(at_least, "nights", 3)({"nights": 2}) is False


def test_normalize_booking() -> None:
    raw = {
        "guest": "  alice smith ",
        "nights": "3",
        "room_type": " Deluxe ",
        "price": "120.5",
        "status": " Confirmed ",
    }
    assert normalize_booking(raw) == {
        "guest": "Alice Smith",
        "nights": 3,
        "room_type": "deluxe",
        "price": 120.5,
        "status": "confirmed",
    }


def test_normalize_booking_rejects_invalid_records() -> None:
    with pytest.raises(ValueError):
        normalize_booking({"guest": "x"})
    with pytest.raises(ValueError):
        normalize_booking(
            {
                "guest": "x",
                "nights": "many",
                "room_type": "r",
                "price": 1,
                "status": "s",
            }
        )


def test_normalize_student() -> None:
    assert normalize_student({"name": "  ALICE ", "age": "19", "score": "8.5"}) == {
        "name": "Alice",
        "age": 19,
        "score": 8.5,
    }


# ---------- singledispatch ----------


def test_loader_json_string_and_csv_string_agree() -> None:
    from_json = load_bookings(BOOKINGS_JSON)
    from_csv = load_bookings(BOOKINGS_CSV)
    assert [normalize_booking(r) for r in from_json] == [
        normalize_booking(r) for r in from_csv
    ]


def test_loader_str_path_path_and_file(tmp_path: Path) -> None:
    json_path = tmp_path / "data.json"
    json_path.write_text(BOOKINGS_JSON, encoding="utf-8")
    csv_path = tmp_path / "data.csv"
    csv_path.write_text(BOOKINGS_CSV, encoding="utf-8")

    expected = load_bookings(BOOKINGS_JSON)
    assert load_bookings(str(json_path)) == expected
    assert load_bookings(json_path) == expected
    with json_path.open(encoding="utf-8") as file:
        assert load_bookings(file) == expected

    csv_expected = load_bookings(BOOKINGS_CSV)
    assert load_bookings(str(csv_path)) == csv_expected
    assert load_bookings(csv_path) == csv_expected
    with csv_path.open(encoding="utf-8") as file:
        assert load_bookings(file) == csv_expected
    assert load_bookings(io.StringIO(BOOKINGS_CSV)) == csv_expected


def test_loader_list_is_validated_and_copied(
    bookings_records: list[dict[str, Any]],
) -> None:
    loaded = load_bookings(bookings_records)
    assert loaded == bookings_records
    assert loaded is not bookings_records
    loaded[0]["guest"] = "changed"
    assert bookings_records[0]["guest"] == " alice smith "
    with pytest.raises(ValueError):
        load_bookings([1, 2, 3])


def test_loader_unsupported_type_and_empty_sources() -> None:
    with pytest.raises(TypeError):
        load_bookings(42)
    with pytest.raises(TypeError):
        load_users(None)
    assert load_bookings([]) == []
    assert load_bookings("[]") == []
    assert load_bookings(io.StringIO("")) == []
    assert parse_records("   ") == []


def test_loader_json_must_be_list_of_dicts() -> None:
    with pytest.raises(ValueError):
        parse_records("[1, 2]")


def test_load_users_and_load_bookings_are_separate_dispatchers() -> None:
    assert load_users is not load_bookings
    assert load_users('[{"name": "x"}]') == [{"name": "x"}]
    assert load_users.dispatch(str) is not load_users.dispatch(object)


def test_loader_missing_file_raises() -> None:
    with pytest.raises(FileNotFoundError):
        load_bookings("no_such_file.csv")


# ---------- конвеєри ----------


def test_top_bookings_json_csv_and_list_agree(
    tmp_path: Path, bookings_records: list[dict[str, Any]]
) -> None:
    csv_path = tmp_path / "data.csv"
    csv_path.write_text(BOOKINGS_CSV, encoding="utf-8")
    from_json = top_bookings(BOOKINGS_JSON, top=5)
    from_csv = top_bookings(csv_path, top=5)
    assert from_json == from_csv
    assert [b.guest for b in from_json] == ["Carol Day", "Eva Moon", "Alice Smith"]
    assert top_bookings(bookings_records, top=5) == [
        b for b in from_json if b.guest != "Eva Moon"
    ]


def test_top_bookings_values() -> None:
    result = top_bookings(BOOKINGS_JSON, top=2, tariff=high_season)
    assert [(b.guest, b.total_price) for b in result] == [
        ("Carol Day", 1260.0),
        ("Eva Moon", 560.0),
    ]
    low = top_bookings(BOOKINGS_JSON, top=1, tariff=low_season)
    assert low[0].total_price == 905.0


def test_top_bookings_filters_and_limits() -> None:
    assert top_bookings(BOOKINGS_JSON, top=0) == []
    assert len(top_bookings(BOOKINGS_JSON, top=100)) == 3
    assert [b.guest for b in top_bookings(BOOKINGS_JSON, min_nights=4)] == [
        "Carol Day",
        "Eva Moon",
    ]
    assert top_bookings("[]") == []
    assert all(b.status == "confirmed" for b in top_bookings(BOOKINGS_JSON, top=10))


def test_top_bookings_does_not_mutate_input(
    bookings_records: list[dict[str, Any]],
) -> None:
    snapshot = [dict(r) for r in bookings_records]
    top_bookings(bookings_records, top=3)
    assert bookings_records == snapshot


def test_to_booking() -> None:
    record: Record = {
        "guest": "A",
        "nights": 1,
        "room_type": "r",
        "price": 10.0,
        "status": "confirmed",
        "total_price": 22.5,
    }
    assert to_booking(record).total_price == 22.5


def test_clean_and_rank_students() -> None:
    result = clean_and_rank(STUDENTS_JSON, top=3)
    assert [r["name"] for r in result] == ["Denis", "Adam", "Alice"]
    assert all(r["age"] >= 18 for r in result)
    assert clean_and_rank(STUDENTS_JSON, top=10)[-1]["name"] == "Carol"
    assert clean_and_rank("[]") == []


# ---------- total_ordering ----------


def make_booking(total: float, nights: int = 1, guest: str = "A") -> Booking:
    return Booking(guest, nights, "r", 1.0, "confirmed", total)


def test_booking_all_comparison_operators() -> None:
    low = make_booking(100.0)
    high = make_booking(200.0)
    assert low < high
    assert low <= high
    assert high > low
    assert high >= low
    assert low != high
    assert low == make_booking(100.0)
    assert low <= make_booking(100.0)
    assert low >= make_booking(100.0)
    assert not low > make_booking(100.0)


def test_booking_tie_breakers() -> None:
    assert make_booking(100.0, nights=1) < make_booking(100.0, nights=2)
    assert make_booking(100.0, 1, "A") < make_booking(100.0, 1, "B")


def test_booking_sorting_max_and_hash() -> None:
    items = [make_booking(300.0), make_booking(100.0), make_booking(200.0)]
    assert [b.total_price for b in sorted(items)] == [100.0, 200.0, 300.0]
    assert max(items).total_price == 300.0
    assert min(items).total_price == 100.0
    assert len({make_booking(1.0), make_booking(1.0), make_booking(2.0)}) == 2


def test_booking_foreign_types_return_not_implemented() -> None:
    booking = make_booking(1.0)
    assert booking.__eq__(5) is NotImplemented
    assert booking.__lt__("x") is NotImplemented
    assert booking != 5
    assert (booking == "x") is False
    with pytest.raises(TypeError):
        operator.lt(booking, 5)
    with pytest.raises(TypeError):
        operator.ge(booking, "x")


def test_box_order_volume_area_width() -> None:
    small = Box(1, 2, 3)
    medium = Box(2, 3, 4)
    large = Box(3, 3, 3)
    assert small < medium < large
    assert sorted([large, small, medium]) == [small, medium, large]
    assert small <= Box(1, 2, 3)
    assert large >= medium
    assert large > small


def test_box_tie_breakers() -> None:
    same_volume_bigger_front = Box(4, 3, 1)
    same_volume_smaller_front = Box(1, 4, 3)
    assert same_volume_bigger_front.w * same_volume_bigger_front.h == 12
    assert same_volume_smaller_front < same_volume_bigger_front
    assert Box(2, 6, 1) < Box(6, 2, 1)


def test_box_equality_hash_and_foreign_types() -> None:
    assert Box(1, 2, 3) == Box(1, 2, 3)
    assert hash(Box(1, 2, 3)) == hash(Box(1, 2, 3))
    assert Box(1, 2, 3) != Box(3, 2, 1)
    assert Box(1, 2, 3).__eq__(1) is NotImplemented
    assert Box(1, 2, 3).__lt__(1) is NotImplemented
    with pytest.raises(TypeError):
        operator.le(Box(1, 2, 3), 7)


# ---------- демонстраційний запуск і зразки даних ----------


def test_sample_files_give_same_result() -> None:
    from_json = top_bookings(DATA_DIR / "sample_data.json", top=10)
    from_csv = top_bookings(DATA_DIR / "sample_data.csv", top=10)
    assert from_json == from_csv
    assert len(from_json) == 4


def test_main_prints_demo(capsys: pytest.CaptureFixture[str]) -> None:
    main()
    out = capsys.readouterr().out
    assert "Carol Day: 1260.0" in out
    assert "json == csv == file: True" in out
    assert "max box: Box(w=3, h=3, d=3)" in out


def test_main_as_script(capsys: pytest.CaptureFixture[str]) -> None:
    runpy.run_path(str(DATA_DIR / "main.py"), run_name="__main__")
    assert "Top-3 (high season)" in capsys.readouterr().out
