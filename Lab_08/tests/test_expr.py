from dataclasses import FrozenInstanceError

import pytest

from eval_ import MAX_ABS, EvalOverflow, eval_expr, eval_expr2
from expr import Add, Bin, Expr, Mul, Num, Num2, SupportsBin
from pretty import render


def test_eval_basic() -> None:
    assert eval_expr(Num(5)) == 5
    assert eval_expr(Add(Num(2), Num(3))) == 5
    assert eval_expr(Mul(Num(2), Num(3))) == 6


def test_eval_nested() -> None:
    ast = Mul(Add(Num(2), Num(3)), Num(4))
    assert eval_expr(ast) == 20


def test_eval_deeply_nested() -> None:
    ast: Expr = Num(1)
    for _ in range(50):
        ast = Add(ast, Num(1))
    assert eval_expr(ast) == 51


def test_eval_negative_and_zero() -> None:
    assert eval_expr(Add(Num(-5), Num(5))) == 0
    assert eval_expr(Mul(Num(-3), Num(4))) == -12
    assert eval_expr(Mul(Num(0), Num(9999))) == 0


def test_eval_overflow() -> None:
    assert eval_expr(Num(MAX_ABS)) == MAX_ABS
    with pytest.raises(EvalOverflow):
        eval_expr(Num(MAX_ABS + 1))
    with pytest.raises(EvalOverflow):
        eval_expr(Mul(Num(200), Num(100)))
    with pytest.raises(EvalOverflow):
        eval_expr(Add(Num(MAX_ABS), Num(1)))


def test_render() -> None:
    ast = Mul(Add(Num(2), Num(3)), Num(4))
    assert render(ast) == "((2 + 3) * 4)"
    assert render(Num(-7)) == "-7"


def test_nodes_are_frozen_and_hashable() -> None:
    node = Add(Num(1), Num(2))
    with pytest.raises(FrozenInstanceError):
        node.left = Num(5)  # type: ignore[misc]
    assert node == Add(Num(1), Num(2))
    assert len({node, Add(Num(1), Num(2)), Mul(Num(1), Num(2))}) == 2


def test_positional_pattern_args() -> None:
    assert Add.__match_args__ == ("left", "right")
    assert Num.__match_args__ == ("value",)


def test_eval_expr2_with_literal_operators() -> None:
    ast = Bin("*", Bin("+", Num2(2), Num2(3)), Num2(4))
    assert eval_expr2(ast) == 20
    assert eval_expr2(Num2(7)) == 7
    assert eval_expr2(Bin("+", Num2(1), Bin("*", Num2(2), Num2(3)))) == 7


def test_bin_satisfies_protocol() -> None:
    node: SupportsBin = Bin("+", Num2(1), Num2(2))
    assert node.op == "+"
    assert node.left == Num2(1)
    assert node.right == Num2(2)
