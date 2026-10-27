"""Чисте обчислення виразів через match/case (базове завдання)."""

from __future__ import annotations

from typing import Final

from expr import Add, Bin, Expr, Expr2, Mul, Num, Num2

MAX_ABS: Final[int] = 10_000


class EvalOverflow(ValueError):
    """Результат вийшов за допустимий діапазон."""


def _check_range(x: int) -> int:
    """Повертає x, якщо він у межах діапазону, інакше піднімає EvalOverflow."""
    if abs(x) > MAX_ABS:
        raise EvalOverflow(f"overflow: {x}")
    return x


def eval_expr(e: Expr) -> int:
    """Обчислює дерево Num | Add | Mul."""
    match e:
        case Num(value=v):
            return _check_range(v)
        case Add(left=a, right=b):
            return _check_range(eval_expr(a) + eval_expr(b))
        case Mul(left=a, right=b):
            return _check_range(eval_expr(a) * eval_expr(b))


def eval_expr2(e: Expr2) -> int:
    """Обчислює дерево Num2 | Bin; оператор розбирається через Literal."""
    match e:
        case Num2(value=v):
            return v
        case Bin(op=op, left=a, right=b):
            match op:
                case "+":
                    return eval_expr2(a) + eval_expr2(b)
                case "*":
                    return eval_expr2(a) * eval_expr2(b)
