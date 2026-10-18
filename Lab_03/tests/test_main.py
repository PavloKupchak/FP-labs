import runpy
from pathlib import Path

import pytest

from main import build_demo_rental, main
from model import Status


def test_build_demo_rental() -> None:
    rental = build_demo_rental()
    assert rental.days == 3
    assert rental.status is Status.BOOKED


def test_main_prints_demo(capsys: pytest.CaptureFixture[str]) -> None:
    main()
    out = capsys.readouterr().out
    assert "same object: False" in out
    assert "frozen: FrozenInstanceError" in out
    assert "meta read-only" in out


def test_main_as_script(capsys: pytest.CaptureFixture[str]) -> None:
    path = Path(__file__).resolve().parent.parent / "main.py"
    runpy.run_path(str(path), run_name="__main__")
    assert "cache:" in capsys.readouterr().out
