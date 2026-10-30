import runpy
from pathlib import Path

import pytest

from main import main


def test_main_prints_receipts(capsys: pytest.CaptureFixture[str]) -> None:
    main()
    out = capsys.readouterr().out
    assert "Receipt #1" in out
    assert "Total: 3030.00" in out


def test_main_as_script(capsys: pytest.CaptureFixture[str]) -> None:
    path = Path(__file__).resolve().parent.parent / "main.py"
    runpy.run_path(str(path), run_name="__main__")
    assert "Receipt #5" in capsys.readouterr().out
