"""Точка входу лабораторної роботи №2, варіант 7."""

import sys
from collections.abc import Sequence

from app import run


def main(argv: Sequence[str] | None = None) -> None:
    """Запуск аналізу товарів складу; аргументи командного рядка необов'язкові."""
    run(argv)


if __name__ == "__main__":
    main(sys.argv[1:])
