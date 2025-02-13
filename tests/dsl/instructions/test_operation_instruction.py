import pytest

from imperiumengine.dsl.context import Context
from imperiumengine.dsl.exceptions import DSLError
from imperiumengine.dsl.instructions.operation import OperationInstruction


def test_operation_instruction_success():
    """
    Testa se a execução de uma operação simples de atribuição atualiza corretamente o contexto.

    Exemplo: Se x é 10 e a operação é "x = x + 5", após a execução espera-se que x seja 15.
    """
    context = Context()
    context.variables["x"] = 10
    op_instr = OperationInstruction("x = x + 5")
    op_instr.execute(context)
    assert context.variables["x"] == 15, "Após a operação, x deve ser atualizado para 15."


def test_operation_instruction_multiple_statements():
    """
    Testa se a execução de uma operação com mais de uma instrução gera DSLError.

    A função safe_exec_statement permite apenas uma única instrução.
    """
    context = Context()
    context.variables["x"] = 10
    op_instr = OperationInstruction("x = x + 5\ny = 2")
    with pytest.raises(DSLError) as excinfo:
        op_instr.execute(context)
    assert "Only one statement is permitted" in str(excinfo.value)


def test_operation_instruction_invalid_assignment_target():
    """
    Testa se a operação com um alvo de atribuição inválido (ex.: tuple unpacking)
    gera DSLError.
    """
    context = Context()
    op_instr = OperationInstruction("x, y = 1, 2")
    with pytest.raises(DSLError) as excinfo:
        op_instr.execute(context)
    assert "Assignment target must be a single variable" in str(excinfo.value)


def test_operation_instruction_print(capsys):
    """
    Testa se uma chamada à função print, permitida pelo safe_exec_statement, é executada corretamente.

    A saída padrão é capturada utilizando o fixture 'capsys' do pytest.
    """
    context = Context()
    # Insere a função print no contexto para que a chamada seja permitida.
    context.variables["print"] = print
    context.variables["x"] = "Hello"
    op_instr = OperationInstruction("print(x)")
    op_instr.execute(context)
    captured = capsys.readouterr().out.strip()
    assert captured == "Hello", "A chamada a print(x) deve produzir 'Hello' na saída padrão."
