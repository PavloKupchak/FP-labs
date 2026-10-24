import runpy
from pathlib import Path

import pytest

from filetree import count_files
from main import build_chain, build_sample_tree, main


def test_build_sample_tree() -> None:
    assert count_files(build_sample_tree()) == 4
    assert count_files(build_chain(3)) == 1


def test_main_prints_demo(capsys: pytest.CaptureFixture[str]) -> None:
    main()
    out = capsys.readouterr().out
    assert "files=4 size=750 height=3" in out
    assert "recursive count_files: RecursionError" in out
    assert "iterative count_files_iter: 1" in out


def test_main_as_script(capsys: pytest.CaptureFixture[str]) -> None:
    path = Path(__file__).resolve().parent.parent / "main.py"
    runpy.run_path(str(path), run_name="__main__")
    assert "recursion limit" in capsys.readouterr().out
