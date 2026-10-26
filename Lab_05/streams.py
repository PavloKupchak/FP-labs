"""Ліниві потоки: генератори, itertools і конвеєр обробки сенсорних даних (варіант 7)."""

from collections import deque
from collections.abc import Callable, Iterable, Iterator
from itertools import accumulate, count, dropwhile, islice, takewhile
from operator import mul
from random import Random
from typing import NamedTuple, TypeVar

T = TypeVar("T")


def fib_stream() -> Iterator[int]:
    """Нескінченний потік чисел Фібоначчі."""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


def naturals(start: int = 1) -> Iterator[int]:
    """Нескінченний потік натуральних чисел."""
    yield from count(start)


def take(n: int, it: Iterable[T]) -> list[T]:
    """Бере перші n елементів; джерело просувається рівно на n кроків."""
    if n < 0:
        raise ValueError("n must be non-negative")
    return list(islice(it, n))


def drop(n: int, it: Iterable[T]) -> Iterator[T]:
    """Пропускає перші n елементів і повертає ітератор на решту."""
    if n < 0:
        raise ValueError("n must be non-negative")
    iterator = iter(it)
    next(islice(iterator, n, n), None)
    return iterator


def _windows(it: Iterable[T], k: int) -> Iterator[tuple[T, ...]]:
    """Генератор вікон без матеріалізації джерела."""
    iterator = iter(it)
    window: deque[T] = deque(maxlen=k)
    for _ in range(k):
        try:
            window.append(next(iterator))
        except StopIteration:
            return
    yield tuple(window)
    for item in iterator:
        window.append(item)
        yield tuple(window)


def sliding_window(it: Iterable[T], k: int) -> Iterator[tuple[T, ...]]:
    """Ковзні вікна розміру k; помилка розміру виявляється одразу."""
    if k <= 0:
        raise ValueError("k must be positive")
    return _windows(it, k)


def moving_average(it: Iterable[float], k: int) -> Iterator[float]:
    """Рухоме середнє по вікнах розміру k."""
    return (sum(window) / k for window in sliding_window(it, k))


def _batches(it: Iterable[T], k: int) -> Iterator[tuple[T, ...]]:
    """Генератор пакетів; останній пакет може бути коротшим."""
    iterator = iter(it)
    while batch := tuple(islice(iterator, k)):
        yield batch


def chunked(it: Iterable[T], k: int) -> Iterator[tuple[T, ...]]:
    """Ліниво ділить потік на пакети розміру k; помилка розміру виявляється одразу."""
    if k <= 0:
        raise ValueError("k must be positive")
    return _batches(it, k)


def prefix_sums(it: Iterable[int]) -> Iterator[int]:
    """Префіксні суми."""
    return accumulate(it)


def prefix_products(it: Iterable[int]) -> Iterator[int]:
    """Префіксні добутки."""
    return accumulate(it, mul)


def running_max(it: Iterable[float]) -> Iterator[float]:
    """Поточний максимум."""
    return accumulate(it, max)


def take_while(predicate: Callable[[T], bool], it: Iterable[T]) -> Iterator[T]:
    """Елементи, поки виконується умова."""
    return takewhile(predicate, it)


def drop_while(predicate: Callable[[T], bool], it: Iterable[T]) -> Iterator[T]:
    """Елементи після першого, що не задовольняє умову."""
    return dropwhile(predicate, it)


def sensor_stream(provider: Callable[[], float]) -> Iterator[float]:
    """Нескінченний потік показів датчика, що постачаються викликом provider."""
    while True:
        yield provider()


def simulated_sensor(
    seed: int = 0, noise_count: int = 5, step: float = 2.5
) -> Iterator[float]:
    """Детермінований датчик: спершу шум близько нуля, далі зростання зі збуренням."""
    rng = Random(seed)
    for _ in range(noise_count):
        yield rng.uniform(0.0, 1.0)
    for k in count(1):
        yield step * k + rng.uniform(-0.5, 0.5)


def drop_noise(readings: Iterable[float], noise_level: float) -> Iterator[float]:
    """Відкидає початкові покази, менші за рівень шуму."""
    return dropwhile(lambda x: abs(x) < noise_level, readings)


def until_alarm(readings: Iterable[float], alarm_level: float) -> Iterator[float]:
    """Бере покази до першого, що досягає аварійного порога."""
    return takewhile(lambda x: x < alarm_level, readings)


def process_sensor(
    readings: Iterable[float],
    *,
    noise_level: float,
    alarm_level: float,
    batch_size: int,
) -> Iterator[tuple[float, ...]]:
    """Лінивий конвеєр: без шуму, до аварійного порога, пакетами фіксованого розміру."""
    cleaned = drop_noise(readings, noise_level)
    safe = until_alarm(cleaned, alarm_level)
    return chunked(safe, batch_size)


class BatchStat(NamedTuple):
    """Статистика пакета показів."""

    minimum: float
    maximum: float
    average: float


def summarize(batch: tuple[float, ...]) -> BatchStat:
    """Мінімум, максимум і середнє пакета."""
    return BatchStat(min(batch), max(batch), sum(batch) / len(batch))


def summarize_batches(
    batches: Iterable[tuple[float, ...]],
) -> Iterator[BatchStat]:
    """Ліниво обчислює статистику кожного пакета."""
    return map(summarize, batches)
