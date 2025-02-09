from imperiumengine.config.logger import LogFactory
from imperiumengine.dsl.context import Context
from imperiumengine.dsl.exceptions import DSLError
from imperiumengine.dsl.market_data import IMarketDataProvider


class DSLInterpreter:
    """
    Interpreta a estratégia definida na DSL.

    Esta classe é responsável por interpretar e executar uma estratégia definida por uma DSL. Ela
    gerencia o contexto de execução, carrega os dados de mercado utilizando um provedor de dados e
    executa a instrução raiz da estratégia. Durante a execução, mensagens de log são registradas para
    facilitar o monitoramento e a depuração.

    Parameters
    ----------
    root_instruction : Instruction
        Instrução raiz que representa a estratégia a ser executada. Essa instrução deve ser uma
        instância de uma classe que implemente o método `execute(context)`.
    market_data_provider : IMarketDataProvider
        Provedor de dados de mercado que será utilizado para carregar os dados necessários à estratégia.
        Esse objeto deve implementar o método `get_market_data(symbol, interval, limit)`.

    Attributes
    ----------
    logger : logging.Logger
        Logger utilizado para registrar informações, avisos e erros durante a execução da estratégia.
    root_instruction : Instruction
        Instrução raiz que define a estratégia DSL.
    market_data_provider : IMarketDataProvider
        Instância do provedor de dados de mercado.
    context : Context
        Contexto de execução que armazena as variáveis utilizadas durante a execução da estratégia.

    Methods
    -------
    load_market_data(symbol: str, interval: str, limit: int) -> None
        Carrega os dados de mercado para um símbolo específico, atualizando o contexto com os dados obtidos.
    run() -> None
        Executa a estratégia DSL chamando o método `execute` da instrução raiz com o contexto atual.

    Examples
    --------
    """

    def __init__(self, root_instruction, market_data_provider: IMarketDataProvider) -> None:
        """

        Inicializa o interpretador DSL com a instrução raiz e o provedor de dados de mercado.

        Parameters
        ----------
        root_instruction : Instruction
            Instrução raiz que define a estratégia a ser executada.
        market_data_provider : IMarketDataProvider
            Provedor de dados de mercado para carregar os dados necessários à execução da estratégia.
        """
        self.logger = LogFactory.get_logger(self.__class__.__name__)
        self.root_instruction = root_instruction
        self.market_data_provider = market_data_provider
        self.context = Context()

        self.logger.info(
            f"DSLInterpreter initialized with root instruction: {type(root_instruction).__name__} "
            f"and market data provider: {type(market_data_provider).__name__}"
        )

    def load_market_data(self, symbol: str, interval: str, limit: int) -> None:
        """
        Carrega os dados de mercado e atualiza o contexto.

        Utiliza o provedor de dados de mercado para obter os dados correspondentes ao símbolo,
        intervalo e limite especificados. Após obter os dados, o contexto de execução é atualizado
        com as informações, permitindo que a estratégia utilize esses dados durante sua execução.

        Parameters
        ----------
        symbol : str
            Símbolo do ativo (ex.: "AAPL") para o qual os dados de mercado serão carregados.
        interval : str
            Intervalo de tempo dos dados (ex.: "1h" para uma hora).
        limit : int
            Número máximo de registros de dados a serem carregados.

        Raises
        ------
        DSLError
            Se ocorrer algum erro durante a obtenção ou atualização dos dados de mercado.
        """
        try:
            self.logger.info(
                f"Loading market data for symbol: {symbol}, interval: {interval}, limit: {limit}"
            )
            market_data = self.market_data_provider.get_market_data(symbol, interval, limit)
            self.context.update(market_data)
            self.logger.info(
                f"Market data loaded successfully. {len(market_data)} records added to context."
            )
        except Exception as e:
            self.logger.exception(
                f"Error loading market data for {symbol} at {interval} with limit {limit}"
            )
            raise DSLError(f"Failed to load market data: {e}") from e

    def run(self) -> None:
        """
        Executa a estratégia DSL.

        Inicia a execução da estratégia chamando o método `execute` da instrução raiz com o contexto
        atual. Durante a execução, mensagens de log são registradas para monitoramento e diagnóstico.
        Em caso de erros durante a execução, as exceções são capturadas, logadas e relançadas como
        `DSLError`.

        Raises
        ------
        DSLError
            Se ocorrer um erro durante a execução da estratégia.
        """
        try:
            self.logger.info("Starting DSL strategy execution...")
            self.root_instruction.execute(self.context)
            self.logger.info("DSL strategy executed successfully.")
        except DSLError as e:
            self.logger.error(f"DSL execution failed: {e}")
            raise
        except Exception as e:
            self.logger.exception("Unexpected error during strategy execution.")
            raise DSLError(f"Unexpected error during strategy execution: {e}") from e
