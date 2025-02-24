from imperiumengine.dsl.context import Context
from imperiumengine.dsl.instructions.instruction import Instruction


class CompoundInstruction(Instruction):
    """
    Representa uma instrução composta que executa uma sequência de instruções.

    Esta classe permite agrupar múltiplas instruções que serão executadas sequencialmente em um mesmo
    contexto. Cada instrução deve ser uma instância de uma classe derivada de `Instruction` e deve
    implementar o método `execute(context)`.

    Parameters
    ----------
    instructions : list of Instruction
        Lista de instruções a serem executadas na ordem definida.

    Attributes
    ----------
    instructions : list of Instruction
        Lista que armazena as instruções que serão executadas sequencialmente.

    Methods
    -------
    execute(context: Context) -> None
        Executa cada instrução presente na lista utilizando o contexto fornecido.

    Examples
    --------
    >>> from imperiumengine.dsl.context import Context
    >>> class DummyInstruction(Instruction):
    ...     def __init__(self, valor):
    ...         self.valor = valor
    ...
    ...     def execute(self, context):
    ...         # Inicializa o atributo 'resultado' se não existir e acumula o valor
    ...         if not hasattr(context, "resultado"):
    ...             context.resultado = 0
    ...         context.resultado += self.valor
    >>> contexto = Context()
    >>> instrucao1 = DummyInstruction(10)
    >>> instrucao2 = DummyInstruction(5)
    >>> instrucao_composta = CompoundInstruction([instrucao1, instrucao2])
    >>> instrucao_composta.execute(contexto)
    >>> contexto.resultado
    15
    """

    def __init__(self, instructions: list[Instruction]) -> None:
        """
        Inicializa a instrução composta com uma lista de instruções.

        Parameters
        ----------
        instructions : list of Instruction
            Lista de instâncias de instruções a serem executadas sequencialmente.
        """
        self.instructions = instructions

    def execute(self, context: Context) -> None:
        """
        Executa cada instrução da lista utilizando o mesmo contexto.

        Itera sobre a lista de instruções e, para cada uma, invoca o método `execute`, passando o
        contexto fornecido como parâmetro. Dessa forma, todas as instruções operam sobre o mesmo
        estado ou conjunto de dados.

        Parameters
        ----------
        context : Context
            Objeto que representa o contexto de execução, contendo os dados ou estado necessário para
            a execução das instruções.

        Returns
        -------
        None
        """
        for instr in self.instructions:
            instr.execute(context)
