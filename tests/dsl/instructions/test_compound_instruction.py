from imperiumengine.dsl.context import Context
from imperiumengine.dsl.instructions.compound_instruction import CompoundInstruction
from imperiumengine.dsl.instructions.instruction import Instruction


class DummyInstruction(Instruction):
    """
    Instrução dummy que acumula um valor no contexto.

    Ao ser executada, essa instrução verifica se o atributo 'resultado' existe no contexto;
    se não existir, o inicializa com zero. Em seguida, incrementa 'resultado' com o valor definido.
    """

    def __init__(self, value: float) -> None:
        self.value = value

    def execute(self, context: Context) -> None:
        if not hasattr(context, "resultado"):
            context.resultado = 0
        context.resultado += self.value


def test_compound_instruction_sum():
    """
    Testa se a CompoundInstruction executa todas as instruções da lista, acumulando corretamente os valores.

    Neste teste, são criadas duas instruções dummy que somam 10 e 5, respectivamente. Após a execução,
    espera-se que o atributo 'resultado' do contexto seja 15.
    """
    contexto = Context()
    instrucao1 = DummyInstruction(10)
    instrucao2 = DummyInstruction(5)
    instrucao_composta = CompoundInstruction([instrucao1, instrucao2])
    instrucao_composta.execute(contexto)
    assert contexto.resultado == 15, "O valor acumulado no contexto deve ser 15."


def test_compound_instruction_empty():
    """
    Testa o comportamento da CompoundInstruction quando não há instruções na lista.

    Neste caso, o contexto não deve ser modificado (ou seja, o atributo 'resultado' não deve ser criado).
    """
    contexto = Context()
    instrucao_composta = CompoundInstruction([])
    instrucao_composta.execute(contexto)
    # Verifica que nenhum atributo 'resultado' foi criado no contexto
    assert not hasattr(contexto, "resultado"), (
        "Nenhuma modificação deve ocorrer no contexto se não houver instruções."
    )
