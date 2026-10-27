"""Текстове представлення виразів і результатів."""

from __future__ import annotations

from typing import Protocol

from expr import Add, Expr, Mul, Num
from model import Failure, Result, Success


class Renders(Protocol):
    """Структурний контракт для об'єктів, що вміють відображати себе."""

    def render(self) -> str: ...


def render(e: Expr) -> str:
    """Повне дужкове представлення виразу."""
    match e:
        case Num(value=v):
            return str(v)
        case Add(left=a, right=b):
            return f"({render(a)} + {render(b)})"
        case Mul(left=a, right=b):
            return f"({render(a)} * {render(b)})"


def render_result(result: Result[object]) -> str:
    """Текстове представлення результату операції."""
    match result:
        case Success(value=value):
            return f"Success({value!r})"
        case Failure(error=error, code=code):
            return f"Failure[{code}]: {error}"
