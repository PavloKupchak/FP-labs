import runpy
from pathlib import Path

import pytest

from main import main


def test_main_prints_demo(capsys: pytest.CaptureFixture[str]) -> None:
    main()
    out = capsys.readouterr().out
    assert "((2 + 3) * 4) = 20" in out
    assert "Failure[overflow]: overflow: 20000" in out
    assert "Success(2.5)" in out
    assert "Failure[division_by_zero]" in out
    assert "unwrap_or: -1" in out
    assert "Success((1, 2, 3))" in out
    assert "Stats(successes=1, failures=2" in out


def test_main_as_script(capsys: pytest.CaptureFixture[str]) -> None:
    path = Path(__file__).resolve().parent.parent / "main.py"
    runpy.run_path(str(path), run_name="__main__")
    assert "map_result: Success(42)" in capsys.readouterr().out
