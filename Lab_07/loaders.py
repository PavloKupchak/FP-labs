"""Поліморфне завантаження записів (JSON і CSV) через functools.singledispatch."""

import csv
import io
import json
from functools import singledispatch
from pathlib import Path
from typing import Any

Records = list[dict[str, Any]]


def _ensure_records(data: Any) -> Records:
    """Перевіряє, що дані є списком словників, і повертає їх копію."""
    if not isinstance(data, list) or not all(isinstance(row, dict) for row in data):
        raise ValueError("Expected a list of dicts")
    return [dict(row) for row in data]


def parse_records(text: str) -> Records:
    """Розбирає текст: JSON, якщо він починається з '[', інакше CSV із заголовком."""
    stripped = text.strip()
    if not stripped:
        return []
    if stripped.startswith("["):
        return _ensure_records(json.loads(stripped))
    return [dict(row) for row in csv.DictReader(io.StringIO(stripped))]


def _load_str(src: str) -> Records:
    """Рядок: вміст (JSON або CSV) чи шлях до файлу."""
    stripped = src.strip()
    if stripped.startswith("[") or "\n" in stripped:
        return parse_records(stripped)
    return parse_records(Path(stripped).read_text(encoding="utf-8"))


def _load_path(src: Path) -> Records:
    """Шлях до файлу .json або .csv."""
    return parse_records(src.read_text(encoding="utf-8"))


def _load_file(src: io.TextIOBase) -> Records:
    """Відкритий текстовий файл."""
    return parse_records(src.read())


def _load_list(src: list[Any]) -> Records:
    """Готова колекція записів: перевіряється й копіюється."""
    return _ensure_records(src)


def _register_handlers(loader: Any) -> None:
    """Реєструє однакові реалізації для str, Path, текстового файлу та list."""
    loader.register(str, _load_str)
    loader.register(Path, _load_path)
    loader.register(io.TextIOBase, _load_file)
    loader.register(list, _load_list)


@singledispatch
def load_users(src: object) -> Records:
    """Завантажує записи користувачів із будь-якого підтримуваного джерела."""
    raise TypeError(f"Unsupported type: {type(src)!r}")


@singledispatch
def load_bookings(src: object) -> Records:
    """Завантажує записи бронювань із будь-якого підтримуваного джерела."""
    raise TypeError(f"Unsupported type: {type(src)!r}")


_register_handlers(load_users)
_register_handlers(load_bookings)
