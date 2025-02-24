from imperiumengine.config.logger import LogFactory
from imperiumengine.dsl.context import Context
from imperiumengine.dsl.instructions.instruction import Instruction


class TradeInstruction(Instruction):
    """
    Executa uma operação de trade e registra os dados no contexto.

    Esta classe representa uma instrução que processa uma operação de trade. Ao ser executada,
    os dados do trade são adicionados à lista de trades presente nas variáveis do contexto.
    Se a chave "trades" não existir no contexto, ela será criada e inicializada como uma lista.

    Parameters
    ----------
    trade_data : dict
        Dicionário contendo os dados do trade. Geralmente, espera-se que contenha chaves como:
          - "action": A ação do trade (por exemplo, "buy" ou "sell").
          - "symbol": O símbolo do ativo (por exemplo, "AAPL").
          - "quantity": A quantidade a ser negociada.

    Attributes
    ----------
    trade_data : dict
        Armazena os dados do trade que serão processados.
    logger : logging.Logger
        Logger utilizado para registrar informações, mensagens de debug e erros durante a execução
        da instrução.

    Methods
    -------
    execute(context: Context) -> None
        Executa a instrução de trade, adicionando os dados do trade à lista de trades presente no contexto.

    Examples
    --------
    >>> from imperiumengine.dsl.context import Context
    >>> from imperiumengine.dsl.instructions.trade import TradeInstruction
    >>> # Criação de um contexto simples com um dicionário de variáveis
    >>> context = Context()
    >>> context.variables = {}
    >>> # Dados do trade a ser executado
    >>> trade_data = {"action": "buy", "symbol": "AAPL", "quantity": 100}
    >>> # Criação da instrução de trade
    >>> trade_instr = TradeInstruction(trade_data)
    >>> # Execução da instrução de trade
    >>> trade_instr.execute(context)
    >>> # Verifica se os dados do trade foram adicionados ao contexto
    >>> context.variables["trades"]
    [{'action': 'buy', 'symbol': 'AAPL', 'quantity': 100}]
    """

    def __init__(self, trade_data: dict) -> None:
        """
        Inicializa a instrução de trade com os dados fornecidos.

        Parameters
        ----------
        trade_data : dict
            Dicionário contendo os dados do trade.
        """
        self.trade_data = trade_data
        self.logger = LogFactory.get_logger(self.__class__.__name__)
        self.logger.info("TradeInstruction instance created with trade data: %s", self.trade_data)

    def execute(self, context: Context) -> None:
        """
        Executa a instrução de trade, registrando os dados no contexto.

        O método adiciona os dados do trade à lista associada à chave "trades" no dicionário
        de variáveis do contexto. Se a chave não existir, ela é criada com uma lista vazia.

        Parameters
        ----------
        context : Context
            Objeto que contém o estado e as variáveis necessárias para a execução da instrução.

        Raises
        ------
        RuntimeError
            Se ocorrer um erro inesperado durante a execução da operação de trade.
        """
        self.logger.debug("Starting trade execution: %s", self.trade_data)

        try:
            trades = context.variables.setdefault("trades", [])
            trades.append(self.trade_data)
            self.logger.info("Trade successfully executed: %s", self.trade_data)

        except Exception as e:
            self.logger.exception("Unexpected error during trade execution: %s", self.trade_data)
            raise RuntimeError(f"Unexpected error executing trade: {e}")
