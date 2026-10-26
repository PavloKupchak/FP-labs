import pytest

from decorators import retries


def test_retries_succeeds_on_third_attempt_without_real_sleep() -> None:
    calls = {"n": 0}
    sleeps: list[float] = []

    @retries(attempts=3, delay=0.0, sleep=sleeps.append)
    def flaky() -> str:
        calls["n"] += 1
        if calls["n"] < 3:
            raise RuntimeError("boom")
        return "ok"

    assert flaky() == "ok"
    assert calls["n"] == 3
    assert len(sleeps) == 2


def test_retries_raises_last_exception_after_all_attempts() -> None:
    calls = {"n": 0}

    @retries(attempts=3, sleep=lambda _: None)
    def always_fails() -> None:
        calls["n"] += 1
        raise ValueError(f"attempt {calls['n']}")

    with pytest.raises(ValueError, match="attempt 3"):
        always_fails()
    assert calls["n"] == 3


def test_retries_only_for_listed_exceptions() -> None:
    calls = {"n": 0}

    @retries(attempts=5, exceptions=(TimeoutError,), sleep=lambda _: None)
    def wrong_error() -> None:
        calls["n"] += 1
        raise KeyError("not retried")

    with pytest.raises(KeyError):
        wrong_error()
    assert calls["n"] == 1


def test_retries_exponential_backoff_is_deterministic() -> None:
    sleeps: list[float] = []

    @retries(attempts=4, delay=0.1, backoff=2.0, sleep=sleeps.append)
    def failing() -> None:
        raise ConnectionError("down")

    with pytest.raises(ConnectionError):
        failing()
    assert sleeps == pytest.approx([0.1, 0.2, 0.4])


def test_retries_jitter_uses_injected_random() -> None:
    sleeps: list[float] = []

    @retries(
        attempts=3,
        delay=1.0,
        jitter=0.5,
        sleep=sleeps.append,
        rand=lambda: 0.5,
    )
    def failing() -> None:
        raise TimeoutError

    with pytest.raises(TimeoutError):
        failing()
    assert sleeps == pytest.approx([1.25, 1.25])


def test_retries_logs_attempts() -> None:
    logs: list[str] = []

    @retries(attempts=2, sleep=lambda _: None, logger=logs.append)
    def failing() -> None:
        raise RuntimeError("x")

    with pytest.raises(RuntimeError):
        failing()
    assert "attempt 1 failed" in logs[0]
    assert "fail after 2 attempts" in logs[1]


def test_retries_single_attempt_does_not_sleep() -> None:
    sleeps: list[float] = []

    @retries(attempts=1, sleep=sleeps.append)
    def failing() -> None:
        raise RuntimeError

    with pytest.raises(RuntimeError):
        failing()
    assert sleeps == []


def test_retries_invalid_attempts() -> None:
    with pytest.raises(ValueError):
        retries(attempts=0)


def test_retries_preserves_metadata_and_arguments() -> None:
    @retries(sleep=lambda _: None)
    def add(a: int, b: int = 0) -> int:
        """Додає числа."""
        return a + b

    assert add.__name__ == "add"
    assert add.__doc__ == "Додає числа."
    assert getattr(add, "__wrapped__", None) is not None
    assert add(2, b=3) == 5
