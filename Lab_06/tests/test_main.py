import runpy
from pathlib import Path

import pytest

from main import main


def test_main_prints_demo(capsys: pytest.CaptureFixture[str]) -> None:
    main()
    out = capsys.readouterr().out
    assert "calls: 4" in out
    assert "CacheInfo(hits=2, misses=2, size=2)" in out
    assert "invalidated: 1" in out
    assert "size=0" in out


def test_main_as_script(capsys: pytest.CaptureFixture[str]) -> None:
    path = Path(__file__).resolve().parent.parent / "main.py"
    runpy.run_path(str(path), run_name="__main__")
    assert "cache:" in capsys.readouterr().out
