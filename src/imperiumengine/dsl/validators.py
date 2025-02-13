import ast

from imperiumengine.config.logger import LogFactory


class StrategyValidator:
    """
    Valida as instruções de estratégia definidas na DSL.

    Esta classe processa uma lista de instruções (cada instrução é um dicionário)
    que definem uma estratégia de trading em uma linguagem específica (DSL). Ela realiza
    validações tanto estruturais quanto sintáticas, tais como:

      - Verificar se cada instrução é um dicionário com uma única chave representando o tipo da
        instrução.
      - Validar instruções condicionais ("if") conferindo se a condição é uma string e se pode ser
        interpretada como uma expressão Python válida.
      - Processar recursivamente blocos aninhados para assegurar que cada "if" seja corretamente
        fechado por um "end".
      - Verificar que as instruções "operation" contêm código Python válido.
      - Confirmar que as instruções "indicator" incluem as chaves obrigatórias e que o indicador
        informado é suportado.
      - Validar que as instruções "trade" possuam os detalhes necessários, garantindo que a ação
        seja "buy" ou "sell".
      - Validar que as instruções "wait" tenham o tempo de espera definido de forma numérica ou
        como string formatada com unidade de tempo (segundos 's', minutos 'm' ou horas 'h').

    Todas as mensagens de erro são registradas via logger e acumuladas em uma lista de erros em nível de classe.
    Dessa forma, mesmo que os métodos sejam chamados de forma estática (como ocorre no DSLParser), os erros serão
    corretamente acumulados.

    Attributes
    ----------
    SUPPORTED_INDICATORS : set
        Conjunto de indicadores suportados. Atualmente, são suportados:
        {"SMA", "EMA", "ATR", "BollingerBands", "MACD", "RSI"}.
    errors : list of str (atributo de classe)
        Lista acumulada de mensagens de erro.
    logger : logging.Logger
        Instância do logger utilizada para registrar informações, avisos e erros.

    Methods
    -------
    validate() -> tuple[bool, list[str]]
        Inicia o processo de validação das instruções da estratégia.
    _validate_block(instructions: list[dict], start: int, *, stop_at_end: bool = False) -> int
        Processa recursivamente um bloco de instruções, tratando o emparelhamento de "if" e "end".
    validate_if(instr: dict, index: int) -> None
        Valida a instrução "if" verificando se a condição é uma string e uma expressão Python válida.
    validate_operation(instr: dict, index: int) -> None
        Valida a instrução "operation", assegurando que o código seja uma string e válido.
    validate_indicator(instr: dict, index: int) -> None
        Valida a instrução "indicator", verificando a existência das chaves necessárias e se o
        indicador é suportado.
    validate_trade(instr: dict, index: int) -> None
        Valida a instrução "trade", garantindo que os dados de trade estejam completos e corretos.
    validate_wait(instr: dict, index: int) -> None
        Valida a instrução "wait", verificando se o tempo de espera está no formato correto.
    append_error(message: str) -> None
        Registra uma mensagem de erro via logger e a adiciona à lista de erros.

    Examples
    --------
    Um exemplo de estratégia válida com bloco condicional e trade:

    >>> instructions = [
    ...     {"if": "price > 100"},
    ...     {"operation": "execute_trade()"},
    ...     {"end": True},
    ...     {"trade": {"action": "buy", "symbol": "AAPL", "quantity": 10}},
    ... ]
    >>> validator = StrategyValidator(instructions)
    >>> is_valid, errs = validator.validate()
    >>> is_valid
    True
    >>> errs
    []

    Um exemplo de estratégia inválida, com condição do "if" não sendo uma string:

    >>> instructions = [{"if": 123}]
    >>> validator = StrategyValidator(instructions)
    >>> is_valid, errs = validator.validate()
    >>> is_valid
    False
    >>> any("condition must be a string" in err for err in errs)
    True
    """

    SUPPORTED_INDICATORS = {"SMA", "EMA", "ATR", "BollingerBands", "MACD", "RSI"}
    errors: list[str] = []  # Erros acumulados em nível de classe
    logger = LogFactory.get_logger("StrategyValidator")  # Logger como atributo de classe

    def __init__(self, instructions_list: list[dict]) -> None:
        """
        Inicializa o StrategyValidator com uma lista de instruções da estratégia.

        Parameters
        ----------
        instructions_list : list of dict
            Lista onde cada elemento é um dicionário representando uma instrução da DSL.
        """
        self.instructions = instructions_list
        StrategyValidator.errors = []  # Reinicia a lista de erros
        StrategyValidator.logger.info("StrategyValidator initialized.")

    def validate(self) -> tuple[bool, list[str]]:
        """
        Valida as instruções da estratégia.

        Percorre a lista de instruções, processando cada uma conforme seu tipo e utilizando
        processamento recursivo para blocos condicionais.

        Returns
        -------
        tuple of (bool, list of str)
            Uma tupla em que o primeiro elemento é True se a estratégia for válida (ou seja, se
            nenhuma inconsistência for encontrada) e o segundo elemento é a lista de mensagens de erro
            acumuladas.

        Examples
        --------
        >>> instructions = [
        ...     {"if": "x > 0"},
        ...     {"operation": "x += 1"},
        ...     {"end": True},
        ... ]
        >>> validator = StrategyValidator(instructions)
        >>> valid, errs = validator.validate()
        >>> valid
        True
        """
        StrategyValidator.logger.info("Starting strategy validation...")
        # Inicia a validação do bloco principal (nível superior), sem esperar "end"
        self._validate_block(self.instructions, 0, stop_at_end=False)
        is_valid = len(StrategyValidator.errors) == 0
        if is_valid:
            StrategyValidator.logger.info("Strategy validation completed successfully.")
        else:
            StrategyValidator.logger.error(
                f"Strategy validation failed with {len(StrategyValidator.errors)} errors."
            )
        return is_valid, StrategyValidator.errors

    @staticmethod
    def validate_if(instr: dict, index: int) -> None:
        """
        Valida a instrução "if".

        Verifica se a condição associada à chave "if" é uma string e se pode ser interpretada
        como uma expressão Python válida.

        Parameters
        ----------
        instr : dict
            Dicionário que contém a instrução "if".
        index : int
            Posição da instrução na lista.
        """
        condition = instr["if"]
        if not isinstance(condition, str):
            message = f"Error at 'if' at position {index}: condition must be a string."
            StrategyValidator.append_error(message)
        else:
            try:
                ast.parse(condition, mode="eval")
            except Exception as e:
                StrategyValidator.append_error(
                    f"Error in condition '{condition}' at position {index}: {e}"
                )

    @staticmethod
    def validate_operation(instr: dict, index: int) -> None:
        """
        Valida a instrução "operation".

        Verifica se a operação é uma string e se o código representa um Python válido.

        Parameters
        ----------
        instr : dict
            Dicionário que contém a instrução "operation".
        index : int
            Posição da instrução na lista.
        """
        op = instr["operation"]
        if not isinstance(op, str):
            StrategyValidator.append_error(
                f"Error in operation at position {index}: must be a string."
            )
        else:
            try:
                ast.parse(op, mode="exec")
            except Exception as e:
                StrategyValidator.append_error(
                    f"Error in operation '{op}' at position {index}: {e}"
                )

    @staticmethod
    def validate_indicator(instr: dict, index: int) -> None:
        """
        Valida a instrução "indicator".

        Verifica a existência da chave "name" e, dependendo do indicador, a existência de chaves
        obrigatórias.

        Parameters
        ----------
        instr : dict
            Dicionário que contém a instrução "indicator".
        index : int
            Posição da instrução na lista.
        """
        data = instr["indicator"]
        if "name" not in data:
            StrategyValidator.append_error(
                f"Error in indicator at position {index}: missing key 'name'."
            )
        else:
            indicator_name = data["name"]
            if indicator_name not in StrategyValidator.SUPPORTED_INDICATORS:
                StrategyValidator.append_error(
                    f"Error in indicator at position {index}: '{indicator_name}' is not supported."
                )
            elif indicator_name != "MACD":
                for key in ["period", "source", "var"]:
                    if key not in data:
                        StrategyValidator.append_error(
                            f"Error in indicator at position {index}: missing key '{key}'."
                        )
            else:
                for key in ["fast", "slow", "signal", "source", "var"]:
                    if key not in data:
                        StrategyValidator.append_error(
                            f"Error in MACD indicator at position {index}: missing key '{key}'."
                        )

    @staticmethod
    def validate_trade(instr: dict, index: int) -> None:
        """
        Valida a instrução "trade".

        Verifica se os dados de trade contêm as chaves obrigatórias ("action", "symbol", "quantity")
        e se a ação informada é válida ("buy" ou "sell").

        Parameters
        ----------
        instr : dict
            Dicionário que contém a instrução "trade".
        index : int
            Posição da instrução na lista.
        """
        data = instr["trade"]
        for key in ["action", "symbol", "quantity"]:
            if key not in data:
                StrategyValidator.append_error(
                    f"Error in trade at position {index}: missing key '{key}'."
                )
        if "action" in data and data["action"] not in ["buy", "sell"]:
            StrategyValidator.append_error(
                f"Error in trade at position {index}: invalid action '{data['action']}'."
            )

    @staticmethod
    def validate_wait(instr: dict, index: int) -> None:
        """
        Valida a instrução "wait".

        Verifica se o tempo de espera é numérico ou uma string com um sufixo de tempo válido
        (s, m ou h).

        Parameters
        ----------
        instr : dict
            Dicionário que contém a instrução "wait".
        index : int
            Posição da instrução na lista.
        """
        value = instr["wait"]
        MIN_WAIT_LENGTH = 2
        if isinstance(value, int | float):
            return
        if isinstance(value, str):
            if len(value) < MIN_WAIT_LENGTH or value[-1].lower() not in ["s", "m", "h"]:
                StrategyValidator.append_error(
                    f"Error in wait at position {index}: invalid format '{value}'."
                )
            else:
                try:
                    float(value[:-1])
                except Exception as e:
                    StrategyValidator.append_error(f"Error in wait at position {index}: {e}")
        else:
            StrategyValidator.append_error(
                f"Error in wait at position {index}: value must be numeric or a string with a unit."
            )

    @staticmethod
    def append_error(message: str) -> None:
        """
        Registra uma mensagem de erro.
        A mensagem é registrada via logger e adicionada à lista de erros acumulada.

        Parameters
        ----------
        message : str
            Mensagem de erro a ser registrada.
        """
        StrategyValidator.errors.append(message)
        StrategyValidator.logger.error(message)

    def _validate_block(
        self, instructions: list[dict], start: int, *, stop_at_end: bool = False
    ) -> int:
        """
        Processa recursivamente um bloco de instruções a partir do índice especificado.

        Se o parâmetro `stop_at_end` for True, o método espera encontrar uma instrução "end" que
        feche o bloco atual; ao encontrá-la, retorna o índice da próxima instrução. Se não houver
        um "end" esperado, registra um erro.

        Parameters
        ----------
        instructions : list of dict
            Lista de instruções da estratégia.
        start : int
            Índice a partir do qual o processamento do bloco se inicia.
        stop_at_end : bool, optional
            Indica se o método deve parar ao encontrar uma instrução "end". O padrão é False.

        Returns
        -------
        int
            O índice da próxima instrução a ser processada após a conclusão do bloco.

        Examples
        --------
        >>> instructions = [
        ...     {"if": "x > 0"},
        ...     {"operation": "x += 1"},
        ...     {"end": True},
        ...     {"trade": {"action": "buy", "symbol": "AAPL", "quantity": 10}},
        ... ]
        >>> validator = StrategyValidator(instructions)
        >>> next_index = validator._validate_block(instructions, 0, stop_at_end=False)
        >>> next_index
        4
        """
        i = start
        while i < len(instructions):
            instr = instructions[i]

            if "if" in instr:
                StrategyValidator.logger.info(f"Validating IF at position {i}")
                StrategyValidator.validate_if(instr, i)
                # Processa recursivamente o bloco condicional, esperando um "end"
                i = self._validate_block(instructions, i + 1, stop_at_end=True)
            elif "end" in instr:
                if stop_at_end:
                    StrategyValidator.logger.info(f"Closing IF block at position {i}")
                    return i + 1  # Fecha o bloco atual e retorna o próximo índice
                self.append_error(f"Unexpected 'end' at position {i} without matching 'if'.")
                i += 1
            elif "operation" in instr:
                StrategyValidator.logger.info(f"Validating OPERATION at position {i}")
                StrategyValidator.validate_operation(instr, i)
                i += 1
            elif "indicator" in instr:
                StrategyValidator.logger.info(f"Validating INDICATOR at position {i}")
                StrategyValidator.validate_indicator(instr, i)
                i += 1
            elif "trade" in instr:
                StrategyValidator.logger.info(f"Validating TRADE at position {i}")
                StrategyValidator.validate_trade(instr, i)
                i += 1
            elif "wait" in instr:
                StrategyValidator.logger.info(f"Validating WAIT at position {i}")
                StrategyValidator.validate_wait(instr, i)
                i += 1
            else:
                StrategyValidator.logger.warning(
                    f"Unknown instruction at position {i} ignored: {instr}"
                )
                i += 1

        if stop_at_end:
            self.append_error(f"Unclosed 'if' block detected starting at position {start}.")
        return i
