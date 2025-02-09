import pytest

from imperiumengine.dsl.context import Context
from imperiumengine.dsl.exceptions import DSLError
from imperiumengine.dsl.instructions.indicator import IndicatorInstruction


def test_sma_indicator_success():
    """
    Testa o cálculo do indicador SMA.

    Para uma lista de preços [10, 12, 11, 13, 12, 14] e período 3,
    espera-se que a SMA seja calculada com base nos últimos 3 valores:
    [13, 12, 14] → média = (13 + 12 + 14) / 3 = 13.0.
    """
    indicator_data = {"name": "SMA", "period": 3, "source": "close", "var": "sma_result"}
    indicador = IndicatorInstruction(indicator_data)
    contexto = Context()
    contexto.variables["close"] = [10, 12, 11, 13, 12, 14]
    indicador.execute(contexto)
    assert contexto.variables["sma_result"] == 13.0


def test_missing_required_param():
    """
    Testa se a ausência de um parâmetro obrigatório gera DSLError.

    Neste caso, a chave "var" está ausente.
    """
    indicator_data = {
        "name": "SMA",
        "period": 3,
        "source": "close",
        # "var" ausente
    }
    indicador = IndicatorInstruction(indicator_data)
    contexto = Context()
    contexto.variables["close"] = [10, 12, 11, 13, 12, 14]
    with pytest.raises(DSLError) as exc_info:
        indicador.execute(contexto)
    assert "Missing 'var'" in str(exc_info.value)


def test_unsupported_indicator():
    """
    Testa se um indicador não suportado gera DSLError.

    Usamos "XYZ" como nome de indicador, que não é tratado pela implementação.
    """
    indicator_data = {"name": "XYZ", "period": 3, "source": "close", "var": "result"}
    indicador = IndicatorInstruction(indicator_data)
    contexto = Context()
    contexto.variables["close"] = [1, 2, 3, 4, 5]
    with pytest.raises(DSLError) as exc_info:
        indicador.execute(contexto)
    assert "not supported" in str(exc_info.value).lower()


def test_macd_missing_keys():
    """
    Testa se a ausência de parâmetros obrigatórios para o indicador MACD gera DSLError.

    Para MACD, os parâmetros "fast", "slow" e "signal" são obrigatórios.
    """
    indicator_data = {
        "name": "MACD",
        # Parâmetros "fast", "slow" e "signal" ausentes
        "source": "close",
        "var": "macd_result",
    }
    indicador = IndicatorInstruction(indicator_data)
    contexto = Context()
    # Fornece dados suficientes para o cálculo, embora os parâmetros faltantes gerem erro.
    contexto.variables["close"] = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    with pytest.raises(DSLError) as exc_info:
        indicador.execute(contexto)
    assert "Missing" in str(exc_info.value)


def test_macd_indicator_success():
    """
    Testa o cálculo do indicador MACD com parâmetros válidos.

    Fornece os parâmetros obrigatórios e dados suficientes. O resultado esperado é
    um dicionário com as chaves "macd", "signal" e "histogram".
    """
    indicator_data = {
        "name": "MACD",
        "fast": 3,
        "slow": 5,
        "signal": 3,
        "source": "close",
        "var": "macd_result",
    }
    indicador = IndicatorInstruction(indicator_data)
    contexto = Context()
    # Fornece uma lista com pelo menos 5 valores (necessário para slow=5)
    contexto.variables["close"] = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    indicador.execute(contexto)
    result = contexto.variables["macd_result"]
    assert isinstance(result, dict)
    for key in ["macd", "signal", "histogram"]:
        assert key in result


def test_rsi_insufficient_data():
    """
    Testa se o indicador RSI levanta DSLError quando há dados insuficientes.

    Para RSI com período 14, é necessário pelo menos 15 valores.
    """
    indicator_data = {"name": "RSI", "period": 14, "source": "close", "var": "rsi_result"}
    indicador = IndicatorInstruction(indicator_data)
    contexto = Context()
    # Fornece apenas 10 valores
    contexto.variables["close"] = list(range(1, 11))
    with pytest.raises(DSLError) as exc_info:
        indicador.execute(contexto)
    assert "Not enough data" in str(exc_info.value)


def test_bollinger_bands_indicator():
    """
    Testa o cálculo das Bandas de Bollinger com parâmetros válidos.

    Para uma lista de preços [1, 2, 3, 4, 5] e período 5, a banda central (SMA) é 3.0.
    O desvio padrão dos 5 valores é aproximadamente 1.5811, resultando em:
      - Banda superior ≈ 3.0 + 2*1.5811 ≈ 6.16
      - Banda inferior ≈ 3.0 - 2*1.5811 ≈ -0.16
    """
    indicator_data = {
        "name": "BollingerBands",
        "period": 5,
        "source": "close",
        "var": "bb_result",
        "multiplier": 2,
    }
    indicador = IndicatorInstruction(indicator_data)
    contexto = Context()
    contexto.variables["close"] = [1, 2, 3, 4, 5]
    indicador.execute(contexto)
    result = contexto.variables["bb_result"]
    assert isinstance(result, dict)
    for key in ["lower", "middle", "upper"]:
        assert key in result
    assert round(result["middle"], 2) == 3.00
    assert round(result["upper"], 2) == 6.16
    assert round(result["lower"], 2) == -0.16


def test_ema_indicator():
    """
    Testa o cálculo do indicador EMA com parâmetros válidos.

    Segundo a documentação, para prices = [1, 2, 3, 4, 5] e período 3, a EMA deve ser 4.0.
    """
    indicator_data = {"name": "EMA", "period": 3, "source": "close", "var": "ema_result"}
    indicador = IndicatorInstruction(indicator_data)
    contexto = Context()
    contexto.variables["close"] = [1, 2, 3, 4, 5]
    indicador.execute(contexto)
    assert contexto.variables["ema_result"] == 4.0
