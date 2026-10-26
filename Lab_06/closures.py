"""Замикання: лічильник, логер, нормалізатор запиту та ключ кешу."""

from collections.abc import Callable, Hashable, Iterable
from typing import Any


def make_counter(start: int = 0) -> Callable[[], int]:
    """Лічильник зі станом у замиканні (nonlocal)."""
    value = start

    def inc() -> int:
        """Збільшує лічильник на одиницю й повертає нове значення."""
        nonlocal value
        value += 1
        return value

    return inc


def make_logger(
    prefix: str, sink: Callable[[str], None] = print
) -> Callable[[str], None]:
    """Логер із префіксом; приймач повідомлень передається ззовні."""

    def log(message: str) -> None:
        """Передає повідомлення з префіксом у приймач."""
        sink(f"[{prefix}] {message}")

    return log


def make_normalizer(
    *, stopwords: Iterable[str] = (), lowercase: bool = True
) -> Callable[[str], str]:
    """Нормалізатор запиту: регістр, зайві пробіли та стоп-слова."""
    ignored = frozenset(w.lower() if lowercase else w for w in stopwords)

    def normalize(query: str) -> str:
        """Повертає запит у канонічному вигляді."""
        text = query.lower() if lowercase else query
        return " ".join(word for word in text.split() if word not in ignored)

    return normalize


def make_query_key(
    normalize: Callable[[str], str],
) -> Callable[[tuple[Any, ...], dict[str, Any]], Hashable]:
    """Ключ кешу: нормалізований запит разом з рештою аргументів."""

    def key(args: tuple[Any, ...], kwargs: dict[str, Any]) -> Hashable:
        """Однакові за змістом запити дають однаковий ключ."""
        query = args[0] if args else kwargs["query"]
        rest = {k: v for k, v in kwargs.items() if k != "query"}
        return (normalize(query), args[1:], tuple(sorted(rest.items())))

    return key
