import json
from pathlib import Path

import pytest

from app import load_readings, main, render_receipt, render_report, run
from core import Reading, process_readings_pure


def test_load_readings(tmp_path: Path) -> None:
    path = tmp_path / "data.json"
    path.write_text(
        json.dumps([{"id": 7, "prev": 1, "curr": 5, "group": "household"}]),
        encoding="utf-8",
    )
    assert load_readings(path) == [
        {"id": 7, "prev": 1.0, "curr": 5.0, "group": "household"}
    ]


def test_render_receipt_and_report(
    sample_readings: list[Reading],
    rates: dict[str, float],
    benefit_shares: dict[str, float],
) -> None:
    result = process_readings_pure(
        sample_readings,
        rates=rates,
        benefit_shares=benefit_shares,
        min_consumption=1.0,
    )
    receipt = render_receipt(result["bills"][0])
    report = render_report(result)
    assert "Receipt #1" in receipt
    assert "600.00" in receipt
    assert "Count: 2" in report
    assert "Total: 1000.00" in report


def test_run_prints_report(capsys: pytest.CaptureFixture[str]) -> None:
    run([{"id": 1, "prev": 0.0, "curr": 10.0, "group": "household"}])
    assert "Receipt #1" in capsys.readouterr().out


def test_main_reads_file_and_prints(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "data.json"
    path.write_text(
        json.dumps([{"id": 2, "prev": 0, "curr": 100, "group": "commercial"}]),
        encoding="utf-8",
    )
    main(path)
    out = capsys.readouterr().out
    assert "Receipt #2" in out
    assert "Total: 650.00" in out
