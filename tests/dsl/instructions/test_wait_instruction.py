import time

import pytest

from imperiumengine.dsl.context import Context
from imperiumengine.dsl.exceptions import DSLError
from imperiumengine.dsl.instructions.wait_instruction import WaitInstruction


def test_wait_numeric_below_min():
    """
    Testa se um valor numérico inferior ao mínimo (ex.: 1 segundo) é ajustado para o tempo mínimo (2 segundos).
    Mede o tempo de execução e verifica se é, pelo menos, 2 segundos.
    """
    context = Context()
    start = time.time()
    w = WaitInstruction(1)  # 1 < MIN_WAIT_LENGTH (2)
    w.execute(context)
    elapsed = time.time() - start
    assert elapsed >= 2, f"Tempo decorrido ({elapsed}) deve ser pelo menos 2 segundos"


def test_wait_string_seconds():
    """
    Testa se um valor de espera passado como string com unidade 's' (ex.: '3s') é interpretado corretamente.
    Mede o tempo de execução e verifica se é, pelo menos, 3 segundos.
    """
    context = Context()
    start = time.time()
    w = WaitInstruction("3s")
    w.execute(context)
    elapsed = time.time() - start
    assert elapsed >= 3, f"Tempo decorrido ({elapsed}) deve ser pelo menos 3 segundos"


def test_wait_numeric_valid():
    """
    Testa se um valor numérico válido (ex.: 5 segundos) é respeitado.
    """
    context = Context()
    start = time.time()
    w = WaitInstruction(5)
    w.execute(context)
    elapsed = time.time() - start
    assert elapsed >= 5, f"Tempo decorrido ({elapsed}) deve ser pelo menos 5 segundos"


def test_wait_invalid_unit():
    """
    Testa se um valor de espera com unidade inválida (ex.: '3x') gera DSLError.
    """
    with pytest.raises(DSLError) as excinfo:
        WaitInstruction("3x")
    assert "Invalid wait unit" in str(excinfo.value)


def test_wait_invalid_type():
    """
    Testa se um valor de espera com tipo inválido (por exemplo, uma lista) gera TypeError.
    """
    with pytest.raises(TypeError) as excinfo:
        WaitInstruction([1, 2, 3])
    assert "Wait value must be numeric or a string with a unit" in str(excinfo.value)


def test_wait_invalid_string_format():
    """
    Testa se um valor de espera com formato inválido (ex.: 'abc') gera DSLError.
    """
    with pytest.raises(DSLError) as excinfo:
        WaitInstruction("abc")
    assert "Invalid wait value" in str(excinfo.value)
