"""Точка входу лабораторної роботи №1, варіант 7."""

from pathlib import Path

from app import main as run_app


def main() -> None:
    """Запуск програми обліку електроенергії на зразку даних readings.json."""
    run_app(Path(__file__).with_name("readings.json"))


if __name__ == "__main__":
    main()
