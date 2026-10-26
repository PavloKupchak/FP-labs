"""Параметризовані декоратори: таймінг, повтори та кеш із TTL та інвалідацією."""

import functools
import random
import threading
import time
from collections.abc import Callable, Hashable
from typing import Any, Literal, NamedTuple, ParamSpec, Protocol, TypeVar, cast

P = ParamSpec("P")
R = TypeVar("R")

KeyFn = Callable[[tuple[Any, ...], dict[str, Any]], Hashable]
Predicate = Callable[[tuple[Any, ...], dict[str, Any]], bool]


def timed(
    label: str | None = None,
    *,
    unit: Literal["s", "ms", "us"] = "ms",
    logger: Callable[[str], None] = print,
    clock: Callable[[], float] = time.perf_counter,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Логує час виконання; логер і годинник передаються ззовні."""
    factors = {"s": 1.0, "ms": 1e3, "us": 1e6}
    if unit not in factors:
        raise ValueError("unit must be one of 's', 'ms', 'us'")
    factor = factors[unit]

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        name = label or func.__name__

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            start = clock()
            try:
                return func(*args, **kwargs)
            finally:
                elapsed = (clock() - start) * factor
                logger(f"[timed] {name} took {elapsed:.3f} {unit}")

        return wrapper

    return decorator


def retries(
    attempts: int = 3,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
    delay: float = 0.0,
    backoff: float = 1.0,
    jitter: float = 0.0,
    *,
    sleep: Callable[[float], None] = time.sleep,
    rand: Callable[[], float] = random.random,
    logger: Callable[[str], None] = lambda _: None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Повторює виклик при винятках; sleep, rand і logger передаються ззовні."""
    if attempts < 1:
        raise ValueError("attempts must be at least 1")

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last: BaseException | None = None
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as error:
                    last = error
                    if attempt == attempts:
                        logger(f"[retries] fail after {attempt} attempts: {error!r}")
                        break
                    noise = rand() * jitter if jitter else 0.0
                    wait = delay * (backoff ** (attempt - 1)) + noise
                    logger(
                        f"[retries] attempt {attempt} failed: {error!r}; "
                        f"sleeping {wait:.3f}s"
                    )
                    sleep(wait)
            assert last is not None
            raise last

        return wrapper

    return decorator


class CacheInfo(NamedTuple):
    """Статистика кешу."""

    hits: int
    misses: int
    size: int


class Cached(Protocol[P, R]):
    """Функція з кешем: виклик та методи керування кешем."""

    __name__: str
    __wrapped__: Callable[P, R]

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R: ...

    def cache_clear(self) -> None: ...

    def cache_invalidate(self, predicate: Predicate) -> int: ...

    def cache_info(self) -> CacheInfo: ...


def make_key(args: tuple[Any, ...], kwargs: dict[str, Any]) -> Hashable:
    """Ключ за замовчуванням: позиційні та відсортовані іменовані аргументи."""
    return (args, tuple(sorted(kwargs.items())))


def cached(
    *,
    ttl: float | None = None,
    time_fn: Callable[[], float] = time.time,
    key_fn: KeyFn = make_key,
) -> Callable[[Callable[P, R]], Cached[P, R]]:
    """Кеш із TTL, власною функцією ключа та інвалідацією за предикатом."""

    def decorator(func: Callable[P, R]) -> Cached[P, R]:
        cache: dict[Hashable, tuple[float | None, R, tuple[Any, ...], dict[str, Any]]]
        cache = {}
        lock = threading.Lock()
        hits = 0
        misses = 0

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            nonlocal hits, misses
            key = key_fn(args, dict(kwargs))
            now = time_fn()
            with lock:
                if key in cache:
                    expiry, value, _, _ = cache[key]
                    if expiry is None or now < expiry:
                        hits += 1
                        return value
                    del cache[key]
                misses += 1
            result = func(*args, **kwargs)
            with lock:
                expiry = None if ttl is None else time_fn() + ttl
                cache[key] = (expiry, result, args, dict(kwargs))
            return result

        def cache_clear() -> None:
            """Повністю очищає кеш і лічильники."""
            nonlocal hits, misses
            with lock:
                cache.clear()
                hits = 0
                misses = 0

        def cache_invalidate(predicate: Predicate) -> int:
            """Видаляє записи, для яких предикат (args, kwargs) істинний."""
            with lock:
                doomed = [k for k, v in cache.items() if predicate(v[2], v[3])]
                for k in doomed:
                    del cache[k]
                return len(doomed)

        def cache_info() -> CacheInfo:
            """Влучання, промахи та поточний розмір кешу."""
            with lock:
                return CacheInfo(hits, misses, len(cache))

        wrapper.cache_clear = cache_clear  # type: ignore[attr-defined]
        wrapper.cache_invalidate = cache_invalidate  # type: ignore[attr-defined]
        wrapper.cache_info = cache_info  # type: ignore[attr-defined]
        return cast(Cached[P, R], wrapper)

    return decorator
