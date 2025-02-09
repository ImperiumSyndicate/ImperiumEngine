import pytest

from imperiumengine.dsl.evaluator import safe_eval_expr
from imperiumengine.dsl.exceptions import DSLError


def test_safe_eval_arithmetic():
    context = {"x": 10, "y": 5}
    result = safe_eval_expr("x + y", context)
    assert result == 15


def test_safe_eval_special_operator():
    """
    Testa a substituição de operador especial '→' por uma chamada de função.
    Para x=True e y=False, implies(True, False) deve retornar False.
    """
    context = {"x": True, "y": False}
    result = safe_eval_expr("x → y", context)
    assert result is False


def test_safe_eval_invalid_syntax():
    context = {"x": 10}
    with pytest.raises(DSLError) as exc_info:
        safe_eval_expr("x +", context)
    assert "Error in safe evaluation" in str(exc_info.value)
