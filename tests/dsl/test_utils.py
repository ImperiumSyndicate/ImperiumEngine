import pytest

from imperiumengine.dsl.exceptions import DSLError
from imperiumengine.dsl.utils import (
    compute_atr,
    compute_bollinger_bands,
    compute_ema,
    compute_ema_series,
    compute_macd,
    compute_rsi,
    compute_sma,
)


# Testes para compute_sma
def test_compute_sma_normal():
    """Teste normal para o cálculo da SMA."""
    # Para os últimos 3 valores de [1, 2, 3, 4, 5]: média = (3+4+5)/3 = 4.0
    assert compute_sma([1, 2, 3, 4, 5], 3) == 4.0


def test_compute_sma_insufficient_data():
    """Verifica se DSLError é lançado quando não há dados suficientes."""
    with pytest.raises(DSLError) as exc_info:
        compute_sma([1, 2], 3)
    assert "Not enough data" in str(exc_info.value)


# Testes para compute_ema
def test_compute_ema_normal():
    """Teste normal para o cálculo da EMA."""
    # Para prices = [1,2,3,4,5] e período 3:
    # valor inicial (SMA dos 3 primeiros): (1+2+3)/3 = 2.0
    # Em seguida, para price 4: ema = 4*0.5 + 2*0.5 = 3.0; para price 5: ema = 5*0.5 + 3*0.5 = 4.0
    assert compute_ema([1, 2, 3, 4, 5], 3) == 4.0


def test_compute_ema_insufficient_data():
    """Verifica se DSLError é lançado para dados insuficientes na EMA."""
    with pytest.raises(DSLError) as exc_info:
        compute_ema([1, 2], 3)
    assert "Not enough data" in str(exc_info.value)


# Testes para compute_atr
def test_compute_atr_normal():
    """Teste normal para o cálculo do ATR."""
    highs = [10, 11, 12, 13]
    lows = [8, 9, 10, 11]
    closes = [9, 10, 11, 12]
    # Com período 3, espera-se: (2+2+2)/3 = 2.0
    assert compute_atr(highs, lows, closes, 3) == 2.0


def test_compute_atr_insufficient_data():
    """Verifica se DSLError é lançado para dados insuficientes no ATR."""
    with pytest.raises(DSLError):
        compute_atr([10, 11], [8, 9], [9, 10], 3)


# Testes para compute_bollinger_bands
def test_compute_bollinger_bands_normal():
    """Teste normal para o cálculo das Bandas de Bollinger."""
    prices = [1, 2, 3, 4, 5]
    bands = compute_bollinger_bands(prices, 5, 2)
    # Segundo o exemplo da docstring:
    # banda do meio (SMA): 3.0
    # Banda superior e inferior aproximadas (com arredondamento):
    assert round(bands["middle"], 2) == 3.0
    assert round(bands["upper"], 2) == 6.16
    assert round(bands["lower"], 2) == -0.16


def test_compute_bollinger_bands_insufficient_data():
    """Verifica se DSLError é lançado quando não há dados suficientes para Bollinger Bands."""
    with pytest.raises(DSLError):
        compute_bollinger_bands([1, 2, 3], 5, 2)


# Testes para compute_ema_series
def test_compute_ema_series_normal():
    """Teste normal para o cálculo da série EMA."""
    # Para prices = [1,2,3,4,5] e período 3, a série deve ser [3.0, 4.0]
    series = compute_ema_series([1, 2, 3, 4, 5], 3)
    assert series == [3.0, 4.0]


def test_compute_ema_series_insufficient_data():
    """Verifica se DSLError é lançado para dados insuficientes na série EMA."""
    with pytest.raises(DSLError):
        compute_ema_series([1, 2], 3)


# Testes para compute_macd
def test_compute_macd_normal():
    """Teste normal para o cálculo do MACD."""
    prices = list(range(1, 10))  # [1,2,3,4,5,6,7,8,9]
    result = compute_macd(prices, fast=3, slow=5, signal=3)
    # Segundo o exemplo da docstring, espera-se:
    # macd = 1.0, signal = 1.0, histogram = 0.0
    assert result["macd"] == 1.0
    assert result["signal"] == 1.0
    assert result["histogram"] == 0.0


def test_compute_macd_insufficient_data():
    """Verifica se DSLError é lançado quando não há dados suficientes para o MACD."""
    with pytest.raises(DSLError):
        compute_macd([1, 2, 3], fast=3, slow=5, signal=3)


# Testes para compute_rsi
def test_compute_rsi_normal():
    """Teste normal para o cálculo do RSI."""
    # Para uma sequência ascendente, espera-se RSI de 100 (pois não há perdas).
    prices = list(range(1, 16))  # 15 valores
    assert compute_rsi(prices) == 100


def test_compute_rsi_insufficient_data():
    """Verifica se DSLError é lançado para dados insuficientes no RSI."""
    with pytest.raises(DSLError):
        compute_rsi([1, 2, 3], 14)
