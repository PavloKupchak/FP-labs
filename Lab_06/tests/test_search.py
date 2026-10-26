from collections.abc import Sequence

import pytest

from closures import make_normalizer
from decorators import Cached
from search import Document, make_search_service, search_documents

CORPUS = (
    Document(1, "Python generators", "lazy evaluation"),
    Document(2, "Python decorators", "closures"),
    Document(3, "Caching", "ttl and invalidation"),
)


class Clock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


def test_search_documents_matches_all_terms() -> None:
    assert [d.id for d in search_documents(CORPUS, "python")] == [1, 2]
    assert [d.id for d in search_documents(CORPUS, "python lazy")] == [1]
    assert search_documents(CORPUS, "rust") == ()


def test_search_documents_edge_cases() -> None:
    assert search_documents(CORPUS, "") == ()
    assert search_documents(CORPUS, "   ") == ()
    assert search_documents([], "python") == ()
    assert search_documents(CORPUS, "python", limit=0) == ()
    assert [d.id for d in search_documents(CORPUS, "python", limit=1)] == [1]
    with pytest.raises(ValueError):
        search_documents(CORPUS, "python", limit=-1)


def build_service(
    calls: list[str], clock: Clock, logs: list[str] | None = None
) -> Cached[..., tuple[Document, ...]]:
    def backend(
        corpus: Sequence[Document], query: str, limit: int
    ) -> tuple[Document, ...]:
        calls.append(query)
        return search_documents(corpus, query, limit)

    def log(message: str) -> None:
        if logs is not None:
            logs.append(message)

    return make_search_service(
        CORPUS,
        normalize=make_normalizer(stopwords={"the"}),
        ttl=10.0,
        time_fn=clock,
        clock=clock,
        logger=log,
        backend=backend,
    )


def test_equivalent_queries_share_one_cache_entry() -> None:
    calls: list[str] = []
    service = build_service(calls, Clock())
    first = service("Python")
    second = service("  python  ")
    third = service("the PYTHON")
    assert first == second == third
    assert calls == ["python"]
    info = service.cache_info()
    assert (info.hits, info.misses, info.size) == (2, 1, 1)


def test_different_limits_are_cached_separately() -> None:
    calls: list[str] = []
    service = build_service(calls, Clock())
    assert len(service("python", 1)) == 1
    assert len(service("python", 5)) == 2
    assert len(service("python", limit=1)) == 1
    assert len(calls) == 3
    service("python", 1)
    assert len(calls) == 3


def test_ttl_expiry_triggers_new_search() -> None:
    calls: list[str] = []
    clock = Clock()
    service = build_service(calls, clock)
    service("python")
    clock.now = 9.0
    service("python")
    assert len(calls) == 1
    clock.now = 11.0
    service("python")
    assert len(calls) == 2


def test_invalidate_by_predicate_and_clear() -> None:
    calls: list[str] = []
    service = build_service(calls, Clock())
    service("python")
    service("caching")
    removed = service.cache_invalidate(lambda args, kwargs: "cach" in args[0].lower())
    assert removed == 1
    service("caching")
    assert calls == ["python", "caching", "caching"]
    service.cache_clear()
    assert service.cache_info().size == 0


def test_timing_is_logged_only_for_real_searches() -> None:
    calls: list[str] = []
    logs: list[str] = []
    service = build_service(calls, Clock(), logs)
    service("python")
    service("PYTHON")
    service("python")
    assert len(logs) == 1
    assert "[timed] search took" in logs[0]


def test_service_preserves_metadata() -> None:
    service = build_service([], Clock())
    assert service.__name__ == "search"
    assert service.__doc__ == "Пошук документів за нормалізованим запитом."
    assert service.__wrapped__ is not None
