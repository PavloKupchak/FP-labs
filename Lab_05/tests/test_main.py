import runpy
from pathlib import Path

import pytest

from main import main


def test_main_prints_demo(capsys: pytest.CaptureFixture[str]) -> None:
    main()
    out = capsys.readouterr().out
    assert "fib: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]" in out
    assert "window sums: [6, 9, 12, 15, 18, 21, 24, 27, 30, 33]" in out
    assert "batch:" in out
    assert "memory:" in out


def test_main_as_script(capsys: pytest.CaptureFixture[str]) -> None:
    path = Path(__file__).resolve().parent.parent / "main.py"
    runpy.run_path(str(path), run_name="__main__")
    assert "fib skip 5 take 8" in capsys.readouterr().out
