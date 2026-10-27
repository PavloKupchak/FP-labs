import pytest

from eval_ import MAX_ABS
from evaluator import (
    attempt,
    check_range,
    code_for,
    combine,
    compute_ratio,
    count_codes,
    eval_safe,
    get_item,
    parse_int,
    safe_div,
    statistics,
)
from expr import Add, Expr, Mul, Num
from model import ErrorCode, Failure, Success


def test_parse_int() -> None:
    assert parse_int("42") == Success(42)
    assert parse_int("  -7 ") == Success(-7)
    failure = parse_int("abc")
    assert isinstance(failure, Failure)
    assert failure.code == "invalid"
    assert parse_int("") == Failure(
        "invalid literal for int() with base 10: ''", "invalid"
    )


def test_safe_div() -> None:
    assert safe_div(10, 4) == Success(2.5)
    assert safe_div(0, 5) == Success(0.0)
    assert safe_div(1, 0) == Failure("division by zero", "division_by_zero")


def test_get_item() -> None:
    config = {"retries": 3}
    assert get_item(config, "retries") == Success(3)
    assert get_item(config, "timeout") == Failure("missing key: 'timeout'", "not_found")
    assert get_item({}, "x") == Failure("missing key: 'x'", "not_found")


def test_compute_ratio_chain() -> None:
    assert compute_ratio("10", "4") == Success(2.5)
    assert compute_ratio("1", "0") == Failure("division by zero", "division_by_zero")
    bad_numerator = compute_ratio("x", "2")
    bad_denominator = compute_ratio("1", "y")
    assert isinstance(bad_numerator, Failure)
    assert isinstance(bad_denominator, Failure)
    assert "'x'" in bad_numerator.error
    assert "'y'" in bad_denominator.error


def test_code_for_exception_types() -> None:
    assert code_for(ZeroDivisionError()) == "division_by_zero"
    assert code_for(OverflowError()) == "overflow"
    assert code_for(KeyError("k")) == "not_found"
    assert code_for(IndexError()) == "not_found"
    assert code_for(ValueError()) == "invalid"
    assert code_for(RuntimeError()) == "invalid"


def test_attempt_catches_only_listed_exceptions() -> None:
    assert attempt(lambda: 1 + 1) == Success(2)
    assert attempt(lambda: first_item([]), catch=(IndexError,)) == Failure(
        "list index out of range", "not_found"
    )
    with pytest.raises(ZeroDivisionError):
        attempt(lambda: 1 / 0, catch=(KeyError,))


def first_item(items: list[int]) -> int:
    return items[0]


def test_check_range_and_combine() -> None:
    assert check_range(MAX_ABS) == Success(MAX_ABS)
    assert check_range(-MAX_ABS - 1) == Failure(f"overflow: {-MAX_ABS - 1}", "overflow")
    assert combine(lambda a, b: a + b, Success(1), Success(2)) == Success(3)
    left = Failure("left")
    assert combine(lambda a, b: a + b, left, Failure("right")) is left
    right = Failure("right")
    assert combine(lambda a, b: a + b, Success(1), right) is right


def test_eval_safe() -> None:
    assert eval_safe(Num(5)) == Success(5)
    assert eval_safe(Mul(Add(Num(2), Num(3)), Num(4))) == Success(20)
    assert eval_safe(Mul(Num(200), Num(100))) == Failure("overflow: 20000", "overflow")
    assert eval_safe(Num(MAX_ABS + 1)) == Failure(
        f"overflow: {MAX_ABS + 1}", "overflow"
    )


def test_eval_safe_propagates_nested_failure() -> None:
    deep = Add(Num(1), Add(Num(2), Mul(Num(MAX_ABS), Num(2))))
    result = eval_safe(deep)
    assert isinstance(result, Failure)
    assert result.code == "overflow"


def test_eval_safe_deeply_nested() -> None:
    ast: Expr = Num(1)
    for _ in range(100):
        ast = Add(ast, Num(1))
    assert eval_safe(ast) == Success(101)


def test_statistics_and_protocol() -> None:
    results = [parse_int("1"), parse_int("x"), compute_ratio("1", "0"), Success(2.0)]
    stats = statistics(results)
    assert stats.successes == 2
    assert stats.failures == 2
    assert stats.by_code == {"invalid": 1, "division_by_zero": 1}
    assert statistics([]) == (0, 0, {})


class Problem:
    """Не Failure, але структурно відповідає протоколу HasError."""

    def __init__(self, code: ErrorCode) -> None:
        self._code = code

    @property
    def error(self) -> str:
        return "problem"

    @property
    def code(self) -> ErrorCode:
        return self._code


def test_count_codes_accepts_any_object_with_error_and_code() -> None:
    assert count_codes([Problem("not_found"), Failure("x", "not_found")]) == {
        "not_found": 2
    }
    assert count_codes([Failure("a", "overflow"), Problem("invalid")]) == {
        "overflow": 1,
        "invalid": 1,
    }
    assert count_codes([]) == {}
