"""Базова модель виразів: Expr = Num | Add | Mul та альтернативна форма з Literal."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol, TypeAlias


@dataclass(frozen=True)
class Num:
    """Числовий літерал."""

    value: int


@dataclass(frozen=True)
class Add:
    """Додавання."""

    left: Expr
    right: Expr


@dataclass(frozen=True)
class Mul:
    """Множення."""

    left: Expr
    right: Expr


Expr: TypeAlias = Num | Add | Mul

Op: TypeAlias = Literal["+", "*"]


@dataclass(frozen=True)
class Num2:
    """Числовий літерал альтернативної моделі."""

    value: int


@dataclass(frozen=True)
class Bin:
    """Бінарний вузол із оператором-літералом."""

    op: Op
    left: Expr2
    right: Expr2


Expr2: TypeAlias = Num2 | Bin


class SupportsBin(Protocol):
    """Структурний контракт для будь-яких бінарних вузлів."""

    @property
    def op(self) -> Op: ...

    @property
    def left(self) -> Expr2: ...

    @property
    def right(self) -> Expr2: ...
