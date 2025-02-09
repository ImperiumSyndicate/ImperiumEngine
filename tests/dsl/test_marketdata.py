import pytest

from imperiumengine.dsl.exceptions import DSLError
from imperiumengine.dsl.market_data import BinanceMarketDataProvider

# Ajuste o caminho conforme a organização do seu projeto.

# --- Fake Clients para simular respostas da API da Binance ---


class FakeClient:
    """
    Simula um cliente da Binance que retorna dados de mercado válidos.
    """

    def __init__(self, *args, **kwargs):
        pass

    def get_klines(self, symbol: str, interval: str, limit: int):
        # Simula a resposta da API com uma lista de klines.
        # Cada kline é uma lista onde os índices usados são:
        #   - índice 2: preço máximo (high)
        #   - índice 3: preço mínimo (low)
        #   - índice 4: preço de fechamento (close)
        #
        # Exemplo: para 2 registros, os dados serão:
        #   Primeiro kline: high = "2.0", low = "0.5", close = "1.5"
        #   Segundo kline: high = "2.5", low = "1.0", close = "2.0"
        return [
            [
                0,
                "1.0",
                "2.0",
                "0.5",
                "1.5",
                "volume",
                "other",
                "other",
                "other",
                "other",
                "other",
                "other",
            ],
            [
                1,
                "1.5",
                "2.5",
                "1.0",
                "2.0",
                "volume",
                "other",
                "other",
                "other",
                "other",
                "other",
                "other",
            ],
        ]


class FakeClientError:
    """
    Simula um cliente da Binance que gera uma exceção ao tentar obter os dados.
    """

    def __init__(self, *args, **kwargs):
        pass

    def get_klines(self, symbol: str, interval: str, limit: int):
        raise Exception("Fake API error")


# --- Fixtures e Testes ---


@pytest.fixture
def provider(monkeypatch) -> BinanceMarketDataProvider:
    """
    Cria uma instância de BinanceMarketDataProvider com credenciais dummy e
    substitui o cliente real pelo FakeClient para simulação de respostas.
    """
    provider = BinanceMarketDataProvider(api_key="dummy", api_secret="dummy")
    monkeypatch.setattr(provider, "client", FakeClient())
    return provider


def test_get_market_data_success(provider: BinanceMarketDataProvider):
    """
    Testa se o método get_market_data retorna corretamente os dados processados.
    """
    symbol = "BTCUSDT"
    interval = "1h"
    limit = 2
    data = provider.get_market_data(symbol, interval, limit)

    # Verifica se o dicionário possui as chaves esperadas
    assert "close" in data
    assert "high" in data
    assert "low" in data

    # Valida os valores (convertidos para float) com base nos dados simulados.
    # Conforme FakeClient:
    #   close_prices: [1.5, 2.0]
    #   high_prices: [2.0, 2.5]
    #   low_prices: [0.5, 1.0]
    assert data["close"] == [1.5, 2.0]
    assert data["high"] == [2.0, 2.5]
    assert data["low"] == [0.5, 1.0]


def test_get_market_data_error(monkeypatch):
    """
    Testa se o método get_market_data levanta DSLError quando ocorre um erro na obtenção dos dados.
    """
    provider = BinanceMarketDataProvider(api_key="dummy", api_secret="dummy")
    # Substitui o cliente por um que gera erro.
    monkeypatch.setattr(provider, "client", FakeClientError())

    with pytest.raises(DSLError) as excinfo:
        provider.get_market_data("BTCUSDT", "1h", 2)

    assert "Error obtaining market data" in str(excinfo.value)
