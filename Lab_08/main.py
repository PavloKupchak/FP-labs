"""Демонстрація ADT виразів та результатів операцій."""

from eval_ import eval_expr
from evaluator import (
    compute_ratio,
    eval_safe,
    flat_map,
    get_item,
    map_result,
    parse_int,
    sequence,
    statistics,
    unwrap_or,
)
from expr import Add, Mul, Num
from pretty import render, render_result


def main() -> None:
    """Показує обчислення виразів, ланцюжки Result і статистику."""
    ast = Mul(Add(Num(2), Num(3)), Num(4))
    print(f"{render(ast)} = {eval_expr(ast)}")
    print(f"safe: {render_result(eval_safe(Mul(Num(200), Num(100))))}")

    print(render_result(compute_ratio("10", "4")))
    print(render_result(compute_ratio("1", "0")))
    print(render_result(compute_ratio("x", "2")))

    doubled = map_result(lambda n: n * 2, parse_int("21"))
    print(f"map_result: {render_result(doubled)}")
    print(f"unwrap_or: {unwrap_or(parse_int('oops'), -1)}")
    config = {"retries": 3}
    print(
        render_result(
            flat_map(lambda n: parse_int(str(n + 1)), get_item(config, "retries"))
        )
    )
    print(render_result(get_item(config, "timeout")))
    print(render_result(sequence([parse_int("1"), parse_int("2"), parse_int("3")])))

    stats = statistics([parse_int("1"), parse_int("x"), compute_ratio("1", "0")])
    print(f"stats: {stats}")


if __name__ == "__main__":
    main()
