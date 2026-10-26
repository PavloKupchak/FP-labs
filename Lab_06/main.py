"""Демонстрація замикань і декораторів: кеш пошуку з інвалідацією."""

from closures import make_counter, make_logger, make_normalizer
from search import Document, make_search_service

CORPUS = (
    Document(1, "Python generators", "lazy evaluation with yield"),
    Document(2, "Python decorators", "closures and higher-order functions"),
    Document(3, "Functional programming", "pure functions in Python"),
    Document(4, "Caching", "ttl and invalidation of results"),
    Document(5, "Itertools", "islice, takewhile and accumulate"),
)


def main() -> None:
    """Показує нормалізацію запитів, кеш-хіти, таймінг та інвалідацію."""
    counter = make_counter()
    logger = make_logger("TIMER")
    normalize = make_normalizer(stopwords={"the", "a", "of"})
    service = make_search_service(CORPUS, normalize=normalize, ttl=30.0, logger=logger)
    calls = 0
    for query in ("Python", "  python  ", "the PYTHON", "caching"):
        calls = counter()
        found = service(query)
        print(f"{query!r} -> {[doc.id for doc in found]}")
    print(f"calls: {calls}")
    print(f"cache: {service.cache_info()}")
    removed = service.cache_invalidate(lambda args, kwargs: "cach" in args[0].lower())
    print(f"invalidated: {removed}")
    print(f"cache after invalidation: {service.cache_info()}")
    service.cache_clear()
    print(f"cache after clear: {service.cache_info()}")


if __name__ == "__main__":
    main()
