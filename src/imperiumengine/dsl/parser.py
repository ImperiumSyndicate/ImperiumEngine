from typing import Any

from imperiumengine.config.logger import LogFactory
from imperiumengine.dsl.exceptions import DSLError
from imperiumengine.dsl.instructions.compound_instruction import CompoundInstruction
from imperiumengine.dsl.instructions.if_instruction import IfInstruction
from imperiumengine.dsl.instructions.indicator import IndicatorInstruction
from imperiumengine.dsl.instructions.operation import OperationInstruction
from imperiumengine.dsl.instructions.trade import TradeInstruction
from imperiumengine.dsl.instructions.wait_instruction import WaitInstruction
from imperiumengine.dsl.validators import StrategyValidator


class DSLParser:
    """
    Analisa uma lista de dicionários de instruções e gera um CompoundInstruction.

    Esta classe é responsável por converter uma lista de dicionários que representam instruções
    da DSL em uma instância de CompoundInstruction. Durante o processo de parsing, são identificados
    diferentes tipos de instruções (como "if", "operation", "indicator", "trade", "wait") e utilizadas
    as respectivas classes de instrução para sua representação. Blocos condicionais são processados de
    forma recursiva, e a presença de instruções "end" é utilizada para delimitar o fim de um bloco "if".

    Se, ao final do parsing, houver instruções não processadas ou se um bloco condicional não for
    devidamente fechado, uma exceção DSLError é levantada.

    Attributes
    ----------
    logger : logging.Logger
        Logger utilizado para registrar mensagens de informação, debug e avisos durante o parsing.
        Definido como atributo de classe.

    Methods
    -------
    parse(instructions_list: list[dict[str, Any]]) -> CompoundInstruction
        Converte uma lista completa de instruções em um CompoundInstruction.
    _parse_block(instructions: list[dict[str, Any]], start: int, *, stop_at_end: bool = False) -> tuple[CompoundInstruction, int]
        Processa recursivamente um bloco de instruções a partir do índice especificado, retornando o
        CompoundInstruction resultante e o índice do final do bloco.

    Raises
    ------
    DSLError
        Se houver instruções não processadas após o parsing ou se um bloco iniciado com "if" não for
        fechado com "end".

    Examples
    --------
    Um exemplo simples de parsing com uma única instrução de operação:

    >>> instructions = [{"operation": "x = 1"}]
    >>> compound = DSLParser.parse(instructions)
    >>> # Verifica se a primeira instrução analisada é do tipo OperationInstruction
    >>> compound.instructions[0].__class__.__name__
    'OperationInstruction'
    """

    logger = LogFactory.get_logger("DSLParser")  # Define o logger como atributo de classe

    def __init__(self):
        """
        Inicializa uma instância de DSLParser.

        Registra a inicialização do parser por meio do logger.

        Examples
        --------
        >>> parser = DSLParser()
        >>> isinstance(parser, DSLParser)
        True
        """
        self.logger.info("DSLParser initialized.")

    @staticmethod
    def parse(instructions_list: list[dict[str, Any]]) -> CompoundInstruction:
        """
        Converte uma lista de instruções em um CompoundInstruction.

        Este método inicia o processo de parsing para a lista completa de instruções da estratégia.
        Ele chama o método auxiliar _parse_block para processar recursivamente as instruções e,
        ao final, verifica se todas as instruções foram processadas. Caso contrário, uma exceção
        DSLError é levantada.

        Parameters
        ----------
        instructions_list : list of dict[str, Any]
            Lista de dicionários onde cada dicionário representa uma instrução da DSL. As chaves dos
            dicionários podem incluir "if", "operation", "indicator", "trade", "wait" e "end".

        Returns
        -------
        CompoundInstruction
            Uma instância de CompoundInstruction contendo todas as instruções analisadas.

        Raises
        ------
        DSLError
            Se houver instruções não processadas após o parsing.

        Examples
        --------
        >>> instructions = [{"operation": "x = 1"}]
        >>> compound = DSLParser.parse(instructions)
        >>> compound.instructions[0].__class__.__name__
        'OperationInstruction'
        """
        DSLParser.logger.info(f"Starting DSL parsing for {len(instructions_list)} instructions.")

        compound, index = DSLParser._parse_block(instructions_list, 0, stop_at_end=False)

        if index != len(instructions_list):
            raise DSLError("Excesso de instruções não processadas.")

        DSLParser.logger.info("DSL parsing completed successfully.")
        return compound

    @staticmethod
    def _parse_block(
        instructions: list[dict[str, Any]], start: int, *, stop_at_end: bool = False
    ) -> tuple[CompoundInstruction, int]:
        """

        Processa recursivamente um bloco de instruções a partir de um índice inicial.

        Este método percorre a lista de instruções iniciando em 'start' e analisa cada instrução.
        Para instruções do tipo "if", o método é chamado recursivamente para processar o bloco
        condicional até que seja encontrada a instrução "end". Outras instruções (como "operation",
        "indicator", "trade" e "wait") são validadas e transformadas em suas respectivas instâncias.
        Instruções não reconhecidas são ignoradas com um aviso no logger.

        Parameters
        ----------
        instructions : list of dict[str, Any]
            Lista de dicionários representando as instruções da DSL.
        start : int
            Índice a partir do qual o processamento do bloco deve iniciar.
        stop_at_end : bool, optional
            Indica se o bloco deve ser finalizado ao encontrar uma instrução "end". O padrão é False.

        Returns
        -------
        tuple
            Uma tupla contendo:
              - CompoundInstruction: o bloco de instruções analisado.
              - int: o próximo índice após o fim do bloco processado.

        Raises
        ------
        DSLError
            Se um bloco iniciado com "if" não for fechado com "end" ou se uma instrução "end" for
            encontrada no nível superior (quando stop_at_end é False).

        Examples
        --------
        >>> instructions = [{"if": "x > 0"}, {"operation": "x = x - 1"}, {"end": None}]
        >>> compound, index = DSLParser._parse_block(instructions, 0, stop_at_end=False)
        >>> index
        3
        >>> compound.instructions[0].__class__.__name__
        'IfInstruction'
        """
        parsed_instructions: list = []
        i = start
        while i < len(instructions):
            instr = instructions[i]

            if "if" in instr:
                DSLParser.logger.info(f"Parsing IF instruction at position {i}.")
                StrategyValidator.validate_if(instr, i)
                block, new_index = DSLParser._parse_block(instructions, i + 1, stop_at_end=True)
                parsed_instructions.append(IfInstruction(instr["if"], block))
                i = new_index

            elif "end" in instr:
                if stop_at_end:
                    DSLParser.logger.info(f"END found at position {i}, closing block.")
                    return CompoundInstruction(parsed_instructions), i + 1
                raise DSLError("Instrução 'end' inesperada no nível superior.")

            elif "operation" in instr:
                DSLParser.logger.info(f"Parsing OPERATION instruction at position {i}.")
                StrategyValidator.validate_operation(instr, i)
                parsed_instructions.append(OperationInstruction(instr["operation"]))
                i += 1

            elif "indicator" in instr:
                DSLParser.logger.info(f"Parsing INDICATOR instruction at position {i}.")
                StrategyValidator.validate_indicator(instr, i)
                parsed_instructions.append(IndicatorInstruction(instr["indicator"]))
                i += 1

            elif "trade" in instr:
                DSLParser.logger.info(f"Parsing TRADE instruction at position {i}.")
                StrategyValidator.validate_trade(instr, i)
                parsed_instructions.append(TradeInstruction(instr["trade"]))
                i += 1

            elif "wait" in instr:
                DSLParser.logger.info(f"Parsing WAIT instruction at position {i}.")
                StrategyValidator.validate_wait(instr, i)
                parsed_instructions.append(WaitInstruction(instr["wait"]))
                i += 1

            else:
                DSLParser.logger.warning(f"Unknown instruction at position {i} ignored: {instr}")
                i += 1

        if stop_at_end:
            raise DSLError(f"Bloco iniciado na posição {start} não foi fechado com 'end'.")

        return CompoundInstruction(parsed_instructions), i
