"""ADT результату операції (варіант 7): Result[T] = Success[T] | Failure."""

from dataclasses import dataclass
from typing import Generic, Literal, Protocol, TypeAlias, TypeVar

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)

ErrorCode: TypeAlias = Literal["invalid", "not_found", "overflow", "division_by_zero"]


@dataclass(frozen=True)
class Success(Generic[T_co]):
    """Успішний результат зі значенням."""

    value: T_co


@dataclass(frozen=True)
class Failure:
    """Помилка з повідомленням і кодом із обмеженого набору."""

    error: str
    code: ErrorCode = "invalid"


Result: TypeAlias = Success[T] | Failure


class HasError(Protocol):
    """Структурний контракт для об'єктів, що описують помилку."""

    @property
    def error(self) -> str: ...

    @property
    def code(self) -> ErrorCode: ...
