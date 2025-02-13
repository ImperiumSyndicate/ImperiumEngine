from imperiumengine.dsl.context import Context
from imperiumengine.dsl.instructions.compound_instruction import CompoundInstruction
from imperiumengine.dsl.instructions.if_instruction import IfInstruction
from imperiumengine.dsl.instructions.instruction import Instruction


class DummyInstruction(Instruction):
    """
    Instrução dummy para testes.

    Ao ser executada, essa instrução incrementa o valor da variável 'counter' no contexto.
    Se 'counter' não existir, ela é inicializada com 0.
    """

    def __init__(self, increment: int = 1) -> None:
        self.increment = increment

    def execute(self, context: Context) -> None:
        context.variables["counter"] = context.variables.get("counter", 0) + self.increment


def test_if_instruction_true():
    """
    Testa a execução de um bloco condicional quando a condição é verdadeira.

    - Define 'x' como 10 e 'counter' como 0 no contexto.
    - A condição "x > 5" é verdadeira, portanto o bloco (composto por uma DummyInstruction)
      deve ser executado, incrementando 'counter' em 1.
    """
    context = Context()
    context.variables = {"x": 10, "counter": 0}

    dummy = DummyInstruction(increment=1)
    compound = CompoundInstruction([dummy])
    if_instr = IfInstruction("x > 5", compound)

    if_instr.execute(context)

    assert context.variables["counter"] == 1, (
        "O bloco condicional deveria ter incrementado 'counter' para 1."
    )


def test_if_instruction_false():
    """
    Testa a execução de um bloco condicional quando a condição é falsa.

    - Define 'x' como 10 e 'counter' como 0 no contexto.
    - A condição "x > 15" é falsa, portanto o bloco não deve ser executado.
    """
    context = Context()
    context.variables = {"x": 10, "counter": 0}

    dummy = DummyInstruction(increment=1)
    compound = CompoundInstruction([dummy])
    if_instr = IfInstruction("x > 15", compound)

    if_instr.execute(context)

    assert context.variables["counter"] == 0, (
        "O bloco não deve ser executado quando a condição é falsa."
    )


def test_if_instruction_multiple_execution():
    """
    Testa que o bloco condicional é executado corretamente e que a execução altera o estado do contexto.

    - Define 'x' como 20 e 'counter' como 0.
    - A condição "x > 10" é verdadeira, e o bloco (com uma DummyInstruction que incrementa em 2)
      deve ser executado, fazendo com que 'counter' passe a valer 2.
    """
    context = Context()
    context.variables = {"x": 20, "counter": 0}

    dummy = DummyInstruction(increment=2)
    compound = CompoundInstruction([dummy])
    if_instr = IfInstruction("x > 10", compound)

    if_instr.execute(context)

    assert context.variables["counter"] == 2, (
        "O bloco condicional deveria ter incrementado 'counter' para 2."
    )
