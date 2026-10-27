"""Чисті операції над Result та безпечні обчислення без None як сигналу помилки."""

import operator
from collections import Counter
from collections.abc import Callable, Iterable, Mapping
from typing import NamedTuple, TypeGuard, TypeVar

from eval_ import MAX_ABS
from expr import Add, Expr, Mul, Num
from model import ErrorCode, Failure, HasError, Result, Success

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


def map_result(f: Callable[[T], U], result: Result[T]) -> Result[U]:
    """Застосовує f до значення успіху; помилку повертає без змін."""
    match result:
        case Success(value=value):
            return Success(f(value))
        case Failure():
            return result


def flat_map(f: Callable[[T], Result[U]], result: Result[T]) -> Result[U]:
    """Ланцюжок обчислень, кожне з яких може завершитись помилкою."""
    match result:
        case Success(value=value):
            return f(value)
        case Failure():
            return result


def unwrap_or(result: Result[T], default: T) -> T:
    """Значення успіху або значення за замовчуванням."""
    match result:
        case Success(value=value):
            return value
        case Failure():
            return default


def flatten(result: Result[Result[T]]) -> Result[T]:
    """Розгортає вкладений результат."""
    match result:
        case Success(value=inner):
            return inner
        case Failure():
            return result


def is_success(result: Result[T]) -> bool:
    """Чи є результат успішним."""
    match result:
        case Success():
            return True
        case Failure():
            return False


def is_failure(result: Result[T]) -> TypeGuard[Failure]:
    """Чи є результат помилкою (звужує тип до Failure)."""
    return not is_success(result)


def sequence(results: Iterable[Result[T]]) -> Result[tuple[T, ...]]:
    """Збирає результати в кортеж; перша помилка перериває збирання."""
    values: list[T] = []
    for item in results:
        match item:
            case Success(value=value):
                values.append(value)
            case Failure():
                return item
    return Success(tuple(values))


def code_for(error: Exception) -> ErrorCode:
    """Код помилки за типом винятку."""
    match error:
        case ZeroDivisionError():
            return "division_by_zero"
        case OverflowError():
            return "overflow"
        case KeyError() | IndexError():
            return "not_found"
        case _:
            return "invalid"


def attempt(
    thunk: Callable[[], T], *, catch: tuple[type[Exception], ...] = (Exception,)
) -> Result[T]:
    """Перетворює виняток обчислення на Failure."""
    try:
        return Success(thunk())
    except catch as error:
        return Failure(str(error), code_for(error))


def parse_int(text: str) -> Result[int]:
    """Розбирає ціле число з рядка."""
    return attempt(lambda: int(text.strip()))


def safe_div(a: float, b: float) -> Result[float]:
    """Ділення без винятків: ділення на нуль дає Failure."""
    return attempt(lambda: a / b)


def get_item(mapping: Mapping[str, T], key: str) -> Result[T]:
    """Пошук за ключем: відсутній ключ дає Failure з кодом not_found."""
    if key in mapping:
        return Success(mapping[key])
    return Failure(f"missing key: {key!r}", "not_found")


def compute_ratio(numerator: str, denominator: str) -> Result[float]:
    """Розбирає два числа та ділить їх; помилки передаються ланцюжком."""
    return flat_map(
        lambda n: flat_map(lambda d: safe_div(n, d), parse_int(denominator)),
        parse_int(numerator),
    )


def check_range(x: int) -> Result[int]:
    """Перевірка діапазону без винятків."""
    if abs(x) > MAX_ABS:
        return Failure(f"overflow: {x}", "overflow")
    return Success(x)


def combine(f: Callable[[T, U], V], left: Result[T], right: Result[U]) -> Result[V]:
    """Поєднує два результати функцією f; помилка лівого має пріоритет."""
    return flat_map(lambda x: map_result(lambda y: f(x, y), right), left)


def eval_safe(e: Expr) -> Result[int]:
    """Обчислює Expr, повертаючи Failure замість винятку при переповненні."""
    match e:
        case Num(value=v):
            return check_range(v)
        case Add(left=a, right=b):
            return flat_map(
                check_range, combine(operator.add, eval_safe(a), eval_safe(b))
            )
        case Mul(left=a, right=b):
            return flat_map(
                check_range, combine(operator.mul, eval_safe(a), eval_safe(b))
            )


class Stats(NamedTuple):
    """Статистика набору результатів."""

    successes: int
    failures: int
    by_code: dict[ErrorCode, int]


def count_codes(errors: Iterable[HasError]) -> dict[ErrorCode, int]:
    """Кількість помилок за кодами (приймає будь-який об'єкт із error і code)."""
    return dict(Counter(item.code for item in errors))


def statistics(results: Iterable[Result[object]]) -> Stats:
    """Кількість успіхів і помилок та розподіл помилок за кодами."""
    items = list(results)
    failures = [item for item in items if is_failure(item)]
    return Stats(len(items) - len(failures), len(failures), count_codes(failures))
