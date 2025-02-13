from imperiumengine.config.logger import LogFactory
from imperiumengine.dsl.context import Context
from imperiumengine.dsl.evaluator import safe_exec_statement
from imperiumengine.dsl.exceptions import DSLError
from imperiumengine.dsl.instructions.instruction import Instruction


class OperationInstruction(Instruction):
    """
    Executa uma operação de código dentro do contexto da DSL.

    Esta classe encapsula uma operação representada por uma string que será executada
    de forma segura através da função `safe_exec_statement`. A operação é avaliada utilizando
    as variáveis presentes no contexto, permitindo a modificação do estado ou a execução de
    lógicas definidas pela DSL.

    Parâmetros
    ----------
    operation : str
        String contendo o código ou operação a ser executada. Essa operação deve ser compatível
        com a sintaxe esperada pelo interpretador da DSL.

    Atributos
    ---------
    operation : str
        Armazena a operação de código que será executada.
    logger : logging.Logger
        Instância do logger utilizada para registrar mensagens, erros e informações durante a execução
        da operação.

    Métodos
    -------
    execute(context: Context) -> None
        Executa a operação de código no contexto fornecido, utilizando as variáveis presentes no
        objeto `Context`.


    Exemplos
    --------
    >>> from imperiumengine.dsl.context import Context
    >>> # Supondo que o contexto possua um atributo 'variables' (um dicionário)
    >>> context = Context()
    >>> context.variables = {"x": 10}
    >>>
    >>> # Criação de uma operação que incrementa a variável 'x'
    >>> context.variables = {"x": 10}
    >>> instrucao_operacao = OperationInstruction("x = x + 5")
    >>> instrucao_operacao.execute(context)
    >>> context.variables["x"]
    15
    """

    def __init__(self, operation: str) -> None:
        """
        Inicializa a instrução de operação com o código a ser executado.

        Parameters
        ----------
        operation : str
            String representando a operação de código que será executada.
        """
        self.operation = operation
        self.logger = LogFactory.get_logger(self.__class__.__name__)
        self.logger.info("OperationInstruction instance created with operation: %s", self.operation)

    def execute(self, context: Context) -> None:
        """
        Executa a operação de código utilizando o contexto fornecido.

        A execução é realizada através da função `safe_exec_statement`, que avalia e executa a
        operação de forma segura, utilizando as variáveis presentes no objeto `context`. Caso a
        execução seja bem-sucedida, uma mensagem de log é registrada. Em caso de erro relacionado à
        DSL (DSLError) ou qualquer outro erro inesperado, a exceção é registrada e propagada.

        Parameters
        ----------
        context : Context
            Objeto que contém as variáveis e o estado necessário para a execução da operação. É
            esperado que o contexto possua um atributo `variables` (do tipo dict) onde os valores
            podem ser modificados.

        Raises
        ------
        DSLError
            Se ocorrer um erro durante a execução da operação, seja ele esperado (DSLError) ou
            inesperado, uma exceção DSLError é levantada.
        """
        self.logger.debug("Starting execution of operation: %s", self.operation)

        try:
            safe_exec_statement(self.operation, context.variables)
            self.logger.info("Successfully executed operation: %s", self.operation)

        except DSLError as e:
            self.logger.error("Execution failed due to DSL error: %s", str(e))
            raise

        except Exception as e:
            self.logger.exception("Unexpected error during operation execution: %s", self.operation)
            raise DSLError(f"Unexpected error executing operation: {e}")
