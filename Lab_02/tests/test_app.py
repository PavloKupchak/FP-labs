import json
from pathlib import Path

import pytest

from app import DEFAULT_DATA, load_items, parse_args, render_report, run
from core import process_inventory, reduce_inventory_stats


def write_data(path: Path) -> Path:
    path.write_text(
        json.dumps(
            [
                {"id": 1, "name": "a", "category": "X", "price": 10, "stock": 3},
                {"id": 2, "name": "b", "category": "Y", "price": 5, "stock": 4},
            ]
        ),
        encoding="utf-8",
    )
    return path


def test_load_items_converts_types(tmp_path: Path) -> None:
    items = load_items(write_data(tmp_path / "data.json"))
    assert items[0] == {
        "id": 1,
        "name": "a",
        "category": "X",
        "price": 10.0,
        "stock": 3,
    }
    assert isinstance(items[0]["price"], float)


def test_load_default_sample_data() -> None:
    assert len(load_items(DEFAULT_DATA)) == 8


def test_parse_args_defaults_and_overrides() -> None:
    defaults = parse_args([])
    assert (defaults.top, defaults.factor, defaults.min_stock) == (3, 1.1, 1)
    custom = parse_args(["--top", "5", "--factor", "2", "--boost-category", "X"])
    assert (custom.top, custom.factor, custom.boost_category) == (5, 2.0, "X")


def test_render_report() -> None:
    items = process_inventory()(load_items(DEFAULT_DATA))
    report = render_report(items[:1], reduce_inventory_stats(items))
    assert report.startswith("1. Laptop")
    assert "count: 7" in report
    assert "avg_value:" in report


def test_run_prints_report(capsys: pytest.CaptureFixture[str]) -> None:
    assert run(["--top", "2"]) == 0
    out = capsys.readouterr().out
    assert "1. Laptop Pro [Electronics] value=5500.00" in out
    assert "2. Monitor 27" in out
    assert "inventory_value:" in out


def test_run_with_custom_data(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run(["--data", str(write_data(tmp_path / "d.json")), "--top", "1", "--factor", "1"])
    out = capsys.readouterr().out
    assert "1. A [X] value=30.00" in out
    assert "count: 2" in out
