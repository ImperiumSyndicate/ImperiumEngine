from __future__ import annotations

from typing import TYPE_CHECKING

from imperiumengine.dsl.context import Context
from imperiumengine.dsl.evaluator import safe_eval_expr
from imperiumengine.dsl.instructions.instruction import Instruction

if TYPE_CHECKING:
    from imperiumengine.dsl.instructions.compound_instruction import CompoundInstruction


class IfInstruction(Instruction):
    """
    Avalia um bloco condicional e executa suas instruções se a condição for verdadeira.


    Esta classe representa uma instrução condicional que avalia uma expressão booleana definida em
    `condition`. Se a expressão, quando avaliada utilizando as variáveis do contexto, retornar um
    valor verdadeiro, o bloco de instruções associado (`block`) é executado.

    Parameters
    ----------
    condition : str
        Expressão condicional a ser avaliada. Essa expressão deve resultar em um valor booleano quando
        avaliada no contexto fornecido.
    block : CompoundInstruction
        Bloco composto de instruções a ser executado se a condição for satisfeita. Deve ser uma
        instância de `CompoundInstruction`.

    Attributes
    ----------
    condition : str
        A expressão condicional que será avaliada.
    block : CompoundInstruction
        O bloco de instruções que será executado se a condição for verdadeira.

    Methods
    -------
    execute(context: Context) -> None
        Avalia a condição e, se o resultado for verdadeiro, executa o bloco de instruções associado.

    Examples
    --------
    >>> from imperiumengine.dsl.context import Context
    >>> from imperiumengine.dsl.instructions.compound_instruction import CompoundInstruction
    >>> from imperiumengine.dsl.instructions.if_instruction import IfInstruction
    >>> from imperiumengine.dsl.instructions.instruction import Instruction
    >>>
    >>> # Definindo uma instrução dummy que incrementa o valor 'counter' no contexto
    >>> class DummyInstruction(Instruction):
    ...     def execute(self, context):
    ...         context.variables["counter"] = context.variables.get("counter", 0) + 1
    >>> # Criação de um bloco composto com a instrução dummy
    >>> block = CompoundInstruction([DummyInstruction()])
    >>>
    >>> # Criação do contexto com variável 'x' para avaliação da condição
    >>> context = Context()
    >>> context.variables = {"x": 10}
    >>>
    >>> # Se x > 5, o bloco é executado e 'counter' é incrementado
    >>> if_instr = IfInstruction("x > 5", block)
    >>> if_instr.execute(context)
    >>> context.variables.get("counter", 0)
    1
    >>>
    >>> # Exemplo com condição falsa: se x > 15, o bloco não é executado
    >>> context.variables = {"x": 10, "counter": 0}
    >>> if_instr = IfInstruction("x > 15", block)
    >>> if_instr.execute(context)
    >>> context.variables.get("counter", 0)
    0
    """

    def __init__(self, condition: str, block: CompoundInstruction) -> None:
        self.condition = condition
        self.block = block

    def execute(self, context: Context) -> None:
        """
        Avalia a condição e executa o bloco de instruções se a condição for verdadeira.

        A avaliação da condição é realizada utilizando a função `safe_eval_expr`, que avalia a expressão
        definida em `condition` com base nas variáveis presentes no objeto `context`. Caso o resultado
        seja avaliado como verdadeiro, o método `execute` do bloco de instruções é invocado.

        Parameters
        ----------
        context : Context
            Objeto que contém as variáveis e o estado necessário para a avaliação da condição e execução
            do bloco de instruções.
        """
        result = safe_eval_expr(self.condition, context.variables)
        if result:
            self.block.execute(context)
