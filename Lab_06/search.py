"""Пошук документів із кешем результатів (варіант 7)."""

import time
from collections.abc import Callable, Sequence
from itertools import islice
from typing import NamedTuple

from closures import make_query_key
from decorators import Cached, cached, timed


class Document(NamedTuple):
    """Документ корпусу."""

    id: int
    title: str
    body: str


Backend = Callable[[Sequence[Document], str, int], tuple[Document, ...]]


def search_documents(
    corpus: Sequence[Document], query: str, limit: int = 5
) -> tuple[Document, ...]:
    """Документи, що містять усі слова запиту (без урахування регістру)."""
    if limit < 0:
        raise ValueError("limit must be non-negative")
    terms = query.lower().split()
    if not terms:
        return ()
    matched = (
        doc
        for doc in corpus
        if all(term in f"{doc.title} {doc.body}".lower() for term in terms)
    )
    return tuple(islice(matched, limit))


def make_search_service(
    corpus: Sequence[Document],
    *,
    normalize: Callable[[str], str],
    ttl: float | None = 60.0,
    time_fn: Callable[[], float] = time.time,
    clock: Callable[[], float] = time.perf_counter,
    logger: Callable[[str], None] = lambda _: None,
    backend: Backend = search_documents,
) -> Cached[..., tuple[Document, ...]]:
    """Збирає пошук із кешем: час вимірюється лише для справжніх обчислень."""
    frozen = tuple(corpus)

    def search(query: str, limit: int = 5) -> tuple[Document, ...]:
        """Пошук документів за нормалізованим запитом."""
        return backend(frozen, normalize(query), limit)

    measured = timed("search", unit="ms", logger=logger, clock=clock)(search)
    return cached(ttl=ttl, time_fn=time_fn, key_fn=make_query_key(normalize))(measured)
