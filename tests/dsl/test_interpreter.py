import pytest

from imperiumengine.dsl.context import Context
from imperiumengine.dsl.exceptions import DSLError
from imperiumengine.dsl.interpreter import DSLInterpreter
from imperiumengine.dsl.market_data import IMarketDataProvider

# --- Dummy Implementations ---


class DummyInstruction:
    """
    Instrução dummy que, ao ser executada, atualiza o contexto definindo a chave 'executed' como True.
    """

    def execute(self, context: Context) -> None:
        context.update({"executed": True})


class DummyFailInstruction:
    """
    Instrução dummy que gera uma exceção ao ser executada.
    """

    def execute(self, context: Context) -> None:
        raise Exception("Dummy instruction error")


class DummyMarketDataProvider(IMarketDataProvider):
    """
    Provedor dummy que retorna dados de mercado válidos.
    """

    def get_market_data(self, symbol: str, interval: str, limit: int) -> dict[str, any]:
        # Retorna dados fictícios: listas com três valores para cada tipo de dado.
        return {"close": [1.5, 2.0, 2.5], "high": [2.0, 2.5, 3.0], "low": [1.0, 1.5, 2.0]}


class DummyMarketDataProviderError(IMarketDataProvider):
    """
    Provedor dummy que simula uma falha ao obter os dados de mercado.
    """

    def get_market_data(self, symbol: str, interval: str, limit: int) -> dict[str, any]:
        raise Exception("Dummy market data error")


# --- Testes para DSLInterpreter ---


def test_load_market_data_success():
    """
    Testa se o método load_market_data carrega corretamente os dados de mercado e atualiza o contexto.
    """
    provider = DummyMarketDataProvider()
    dummy_instruction = DummyInstruction()
    interpreter = DSLInterpreter(root_instruction=dummy_instruction, market_data_provider=provider)

    interpreter.load_market_data("AAPL", "1h", 3)

    # Verifica se o contexto foi atualizado com as chaves esperadas
    context_vars = interpreter.context.variables
    assert "close" in context_vars
    assert "high" in context_vars
    assert "low" in context_vars
    assert context_vars["close"] == [1.5, 2.0, 2.5]


def test_load_market_data_error(monkeypatch):
    """
    Testa se load_market_data levanta DSLError quando o provedor de dados gera uma exceção.
    """
    provider = DummyMarketDataProviderError()
    dummy_instruction = DummyInstruction()
    interpreter = DSLInterpreter(root_instruction=dummy_instruction, market_data_provider=provider)

    with pytest.raises(DSLError) as exc_info:
        interpreter.load_market_data("AAPL", "1h", 3)

    # Verifica se a mensagem de erro contém a indicação da falha no carregamento
    assert "Failed to load market data" in str(exc_info.value) or "Dummy market data error" in str(
        exc_info.value
    )


def test_run_success():
    """
    Testa se o método run executa a estratégia com sucesso, atualizando o contexto conforme esperado.
    """
    provider = DummyMarketDataProvider()
    dummy_instruction = DummyInstruction()
    interpreter = DSLInterpreter(root_instruction=dummy_instruction, market_data_provider=provider)

    # Verifica que a chave 'executed' não existe inicialmente.
    assert "executed" not in interpreter.context.variables

    interpreter.run()

    # Após a execução, o dummy deve ter atualizado o contexto
    assert interpreter.context.variables.get("executed", False) is True


def test_run_failure():
    """
    Testa se o método run trata exceções geradas pela instrução raiz e levanta DSLError.
    """
    provider = DummyMarketDataProvider()
    failing_instruction = DummyFailInstruction()
    interpreter = DSLInterpreter(
        root_instruction=failing_instruction, market_data_provider=provider
    )

    with pytest.raises(DSLError) as exc_info:
        interpreter.run()

    # O DSLInterpreter converte exceções inesperadas em DSLError
    assert "Dummy instruction error" in str(exc_info.value)
