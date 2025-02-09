from imperiumengine.dsl.context import Context
from imperiumengine.dsl.instructions.instruction import Instruction


class DummyInstruction(Instruction):
    """
    Subclasse dummy de Instruction para teste.

    Ao ser executada, essa instrução atualiza o atributo 'dummy' do contexto para o valor 'executado'.
    """

    def execute(self, context: Context) -> None:
        # Se o atributo 'variables' não existir, cria-o.
        if not hasattr(context, "variables"):
            context.variables = {}
        context.variables["dummy"] = "executado"


class DummyContext(Context):
    """
    Contexto dummy que inicializa o atributo 'variables' como um dicionário vazio.
    """

    def __init__(self):
        self.variables = {}


def test_dummy_instruction_execution():
    """
    Testa se a execução de DummyInstruction atualiza corretamente o contexto.

    Após a execução, o contexto deve conter a chave 'dummy' com valor 'executado'.
    """
    context = DummyContext()
    instr = DummyInstruction()
    instr.execute(context)
    assert context.variables.get("dummy") == "executado", (
        "A instrução deveria definir 'dummy' como 'executado'."
    )
