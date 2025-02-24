from abc import ABC, abstractmethod

from binance.client import Client

from imperiumengine.config.logger import LogFactory
from imperiumengine.dsl.exceptions import DSLError


class IMarketDataProvider(ABC):
    """
    Interface para provedores de dados de mercado.

    Esta interface define o contrato que deve ser implementado por qualquer classe que forneça
    dados de mercado para a estratégia DSL. A implementação deve fornecer o método
    `get_market_data`, que obtém os dados de mercado para um determinado símbolo, intervalo e
    quantidade máxima de registros.

    Methods
    -------
    get_market_data(symbol: str, interval: str, limit: int) -> dict[str, any]
        Obtém os dados de mercado para o símbolo, intervalo e limite especificados.

    Raises
    ------
    DSLError
        Se ocorrer um erro durante a obtenção dos dados de mercado.
    """

    @abstractmethod
    def get_market_data(self, symbol: str, interval: str, limit: int) -> dict[str, any]:
        """
        Obtém os dados de mercado para o símbolo, intervalo e limite especificados.

        Parameters
        ----------
        symbol : str
            Símbolo do ativo para o qual os dados de mercado serão obtidos (ex.: "BTCUSDT").
        interval : str
            Intervalo de tempo para os dados de mercado (ex.: "1h", "1d").
        limit : int
            Número máximo de registros de dados a serem retornados.

        Returns
        -------
        dict[str, any]
            Dicionário contendo os dados de mercado. A estrutura do dicionário dependerá da implementação,
            mas normalmente inclui listas de preços de fechamento, máxima e mínima.

        Raises
        ------
        DSLError
            Se ocorrer um erro na obtenção dos dados de mercado.
        """


class BinanceMarketDataProvider(IMarketDataProvider):
    """
    Implementação de provedor de dados de mercado utilizando a API da Binance.

    Esta classe utiliza a biblioteca `binance.client.Client` para se conectar à API da Binance e
    obter os dados de mercado (klines) para um símbolo específico. Os dados obtidos são processados
    para extrair as listas de preços de fechamento, máxima e mínima.

    Parameters
    ----------
    api_key : str, optional
        Chave de API para autenticação na Binance. Valor padrão é uma string vazia.
    api_secret : str, optional
        Segredo da API para autenticação na Binance. Valor padrão é uma string vazia.

    Attributes
    ----------
    client : Client
        Instância do cliente Binance utilizada para obter os dados de mercado.
    logger : logging.Logger
        Logger utilizado para registrar informações, avisos e erros durante a execução.

    Methods
    -------
    get_market_data(symbol: str, interval: str, limit: int) -> dict[str, any]
        Obtém os dados de mercado (klines) para o símbolo, intervalo e limite especificados e
        retorna um dicionário com listas de preços de fechamento, alta e baixa.

    Raises
    ------
    DSLError
        Se ocorrer um erro durante a inicialização do cliente ou na obtenção dos dados de mercado.
    """

    def __init__(self, api_key: str = "", api_secret: str = "") -> None:
        """
        Inicializa a instância do BinanceMarketDataProvider.

        Tenta criar uma instância do cliente Binance utilizando as credenciais fornecidas.
        Caso ocorra algum erro durante a inicialização, uma exceção `DSLError` é lançada.

        Parameters
        ----------
        api_key : str, optional
            Chave de API para autenticação na Binance. Valor padrão é uma string vazia.
        api_secret : str, optional
            Segredo da API para autenticação na Binance. Valor padrão é uma string vazia.

        Raises
        ------
        DSLError
            Se ocorrer um erro ao inicializar o cliente da Binance.
        """
        self.logger = LogFactory.get_logger(self.__class__.__name__)

        try:
            self.client = Client(api_key, api_secret)
            self.logger.info("BinanceMarketDataProvider initialized successfully.")
        except Exception as e:
            self.logger.exception("Failed to initialize Binance client.")
            raise DSLError(f"Failed to initialize Binance client: {e}") from e

    def get_market_data(self, symbol: str, interval: str, limit: int) -> dict[str, any]:
        """
        Obtém os dados de mercado para um símbolo utilizando a API da Binance.

        Este método utiliza o cliente Binance para buscar os dados de mercado (klines) para o símbolo
        especificado, em um intervalo de tempo definido e com um limite de registros. A partir dos
        klines, são extraídas as listas de preços de fechamento, máxima e mínima.

        Parameters
        ----------
        symbol : str
            Símbolo do ativo para o qual os dados serão obtidos (ex.: "BTCUSDT").
        interval : str
            Intervalo de tempo dos dados (ex.: "1h" para uma hora, "1d" para um dia).
        limit : int
            Número máximo de registros de dados a serem retornados.

        Returns
        -------
        dict[str, any]
            Dicionário contendo os dados de mercado com as seguintes chaves:
                - "close": lista de preços de fechamento.
                - "high": lista de preços máximos.
                - "low": lista de preços mínimos.

        Raises
        ------
        DSLError
            Se ocorrer um erro ao obter os dados de mercado da Binance.
        """
        self.logger.info(f"Fetching market data for {symbol}, interval {interval}, limit {limit}")

        try:
            klines = self.client.get_klines(symbol=symbol, interval=interval, limit=limit)
            close_prices = [float(kline[4]) for kline in klines]
            high_prices = [float(kline[2]) for kline in klines]
            low_prices = [float(kline[3]) for kline in klines]

            self.logger.info(
                f"Successfully retrieved {len(close_prices)} price entries for {symbol}"
            )

            return {"close": close_prices, "high": high_prices, "low": low_prices}

        except Exception as e:
            self.logger.exception(
                f"Error obtaining market data from Binance for {symbol}, interval {interval}"
            )
            raise DSLError(f"Error obtaining market data: {e}") from e
