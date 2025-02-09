from abc import ABC, abstractmethod

from imperiumengine.dsl.context import Context


class Instruction(ABC):
    """
    Classe base abstrata para instruções na DSL.

    Esta classe define a interface que todas as instruções devem implementar. Cada instrução
    deve fornecer sua própria implementação do método `execute(context)`, que contém a lógica
    para executar a instrução utilizando o contexto fornecido.


    Methods
    -------
    execute(context: Context) -> None
        Executa a instrução utilizando o contexto passado como parâmetro.

    Examples
    --------
    A seguir, um exemplo de como criar uma subclasse de `Instruction` e implementar o método
    `execute`:

    >>> from imperiumengine.dsl.context import Context
    >>> class DummyInstruction(Instruction):
    ...     def execute(self, context: Context) -> None:
    ...         # Supondo que o objeto Context possua um atributo 'variables' do tipo dict.
    ...         context.variables["dummy"] = "executado"
    >>> # Criação de um contexto dummy com um atributo 'variables'
    >>> class DummyContext(Context):
    ...     def __init__(self):
    ...         self.variables = {}
    >>> contexto = DummyContext()
    >>> instrucao = DummyInstruction()
    >>> instrucao.execute(contexto)
    >>> contexto.variables["dummy"]
    'executado'
    """

    @abstractmethod
    def execute(self, context: Context) -> None:
        """
        Executa a instrução utilizando o contexto fornecido.

        Este método deve ser implementado pelas subclasses de `Instruction`. A implementação
        deve definir a lógica de execução da instrução, podendo modificar o estado ou as variáveis
        do objeto `context`.

        Parameters
        ----------
        context : Context
            Objeto que contém o estado e as variáveis necessárias para a execução da instrução.

        Raises
        ------
        NotImplementedError
            Se a subclasse não implementar este método.
        """
