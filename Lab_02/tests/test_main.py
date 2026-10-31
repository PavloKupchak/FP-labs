import runpy
import sys
from pathlib import Path

import pytest

from main import main


def test_main_prints_report(capsys: pytest.CaptureFixture[str]) -> None:
    main([])
    out = capsys.readouterr().out
    assert "1. Laptop Pro" in out
    assert "avg_value:" in out


def test_main_as_script(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sys, "argv", ["main.py"])
    path = Path(__file__).resolve().parent.parent / "main.py"
    runpy.run_path(str(path), run_name="__main__")
    assert "count: 7" in capsys.readouterr().out
