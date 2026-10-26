from closures import make_counter, make_logger, make_normalizer, make_query_key


def test_counter_keeps_state() -> None:
    counter = make_counter(10)
    assert counter() == 11
    assert counter() == 12


def test_counters_are_independent() -> None:
    first = make_counter()
    second = make_counter(100)
    assert first() == 1
    assert first() == 2
    assert second() == 101
    assert first() == 3


def test_logger_prefix_and_sink() -> None:
    lines: list[str] = []
    info = make_logger("INFO", lines.append)
    info("ready")
    assert lines == ["[INFO] ready"]


def test_normalizer_basic() -> None:
    normalize = make_normalizer()
    assert normalize("  Python   LAZY ") == "python lazy"
    assert normalize("") == ""
    assert normalize("   ") == ""


def test_normalizer_stopwords() -> None:
    normalize = make_normalizer(stopwords={"The", "of"})
    assert normalize("The Lord of the Rings") == "lord rings"
    assert normalize("the of") == ""


def test_normalizer_case_sensitive() -> None:
    normalize = make_normalizer(lowercase=False, stopwords={"the"})
    assert normalize("The the cat") == "The cat"


def test_normalizer_unicode() -> None:
    normalize = make_normalizer()
    assert normalize("  Київ   ЛЬВІВ ") == "київ львів"


def test_query_key_ignores_spacing_and_case() -> None:
    key = make_query_key(make_normalizer())
    assert key(("Python",), {}) == key(("  python ",), {})
    assert key(("python",), {}) != key(("java",), {})


def test_query_key_handles_keyword_and_extra_arguments() -> None:
    key = make_query_key(make_normalizer())
    assert key((), {"query": "Python"}) == key((), {"query": " python"})
    assert key(("python", 5), {}) != key(("python", 10), {})
    assert key(("python",), {"limit": 3}) != key(("python",), {"limit": 4})
