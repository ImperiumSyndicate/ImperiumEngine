import statistics

from imperiumengine.dsl.exceptions import DSLError


def compute_sma(prices: list[float], period: int) -> float:
    """
    Calcula a Média Móvel Simples (SMA) para uma lista de preços.

    A SMA é definida como a média aritmética dos últimos ``period`` valores da lista de preços.
    Se a quantidade de preços for menor que o período especificado, uma exceção DSLError é levantada.

    Parameters
    ----------
    prices : list of float
        Lista de preços.
    period : int
        Período utilizado para o cálculo da média.

    Returns
    -------
    float
        Valor da Média Móvel Simples calculada.

    Raises
    ------
    DSLError
        Se o número de preços for insuficiente para o período solicitado.

    Examples
    --------
    >>> compute_sma([1, 2, 3, 4, 5], 3)
    4.0
    """
    if len(prices) < period:
        raise DSLError(f"Not enough data to calculate SMA with period {period}.")
    return sum(prices[-period:]) / period


def compute_ema(prices: list[float], period: int) -> float:
    """
    Calcula a Média Móvel Exponencial (EMA) para uma lista de preços.

    A EMA é calculada utilizando a SMA dos primeiros ``period`` valores como ponto de partida,
    e aplicando um fator de suavização em cada valor subsequente. Se a quantidade de preços for
    insuficiente para o período, uma exceção DSLError é levantada.

    Parameters
    ----------
    prices : list of float
        Lista de preços.
    period : int
        Período para o cálculo da EMA.

    Returns
    -------
    float
        Valor da Média Móvel Exponencial calculada.

    Raises
    ------
    DSLError
        Se o número de preços for insuficiente para o período solicitado.

    Examples
    --------
    >>> compute_ema([1, 2, 3, 4, 5], 3)
    4.0
    """
    if len(prices) < period:
        raise DSLError(f"Not enough data to calculate EMA with period {period}.")
    k = 2 / (period + 1)
    ema = compute_sma(prices[:period], period)  # Usa a média simples como primeiro valor
    for price in prices[period:]:
        ema = price * k + ema * (1 - k)
    return ema


def compute_atr(highs: list[float], lows: list[float], closes: list[float], period: int) -> float:
    """
    Calcula a Média de Intervalo Verdadeiro (ATR) a partir das listas de preços máximos, mínimos e de fechamento.

    O ATR é obtido calculando o True Range (TR) para cada período e, em seguida, fazendo a média dos
    últimos ``period`` valores de TR. Se a quantidade de dados for insuficiente, uma exceção DSLError é levantada.

    Parameters
    ----------
    highs : list of float
        Lista de preços máximos.
    lows : list of float
        Lista de preços mínimos.
    closes : list of float
        Lista de preços de fechamento.
    period : int
        Período utilizado para o cálculo do ATR.

    Returns
    -------
    float
        Valor do ATR calculado.

    Raises
    ------
    DSLError
        Se a quantidade de dados for insuficiente para o período solicitado.

    Examples
    --------
    >>> highs = [10, 11, 12, 13]
    >>> lows = [8, 9, 10, 11]
    >>> closes = [9, 10, 11, 12]
    >>> compute_atr(highs, lows, closes, 3)
    2.0
    """
    if len(closes) < period + 1:
        raise DSLError(f"Not enough data to calculate ATR with period {period}.")

    true_ranges = [
        max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1]))
        for i in range(1, len(closes))
    ]

    if len(true_ranges) < period:
        raise DSLError(f"Not enough TR values to calculate ATR with period {period}.")

    return sum(true_ranges[-period:]) / period


def compute_bollinger_bands(
    prices: list[float], period: int, multiplier: float
) -> dict[str, float]:
    """
    Calcula as Bandas de Bollinger para uma lista de preços.

    As Bandas de Bollinger são compostas pela média móvel simples (banda do meio) e pelas bandas
    superior e inferior, que são definidas como a média mais (ou menos) o ``multiplier`` vezes o
    desvio padrão dos últimos ``period`` valores. Se a quantidade de preços for insuficiente,
    uma exceção DSLError é levantada.

    Parameters
    ----------
    prices : list of float
        Lista de preços.
    period : int
        Período utilizado para o cálculo da média e do desvio padrão.
    multiplier : float
        Fator multiplicador para o desvio padrão, utilizado no cálculo das bandas superior e inferior.

    Returns
    -------
    dict of {str: float}
        Dicionário com as chaves "lower", "middle" e "upper", representando, respectivamente,
        a banda inferior, a banda central (média) e a banda superior.

    Raises
    ------
    DSLError
        Se o número de preços for insuficiente para o período solicitado.

    Examples
    --------
    >>> prices = [1, 2, 3, 4, 5]
    >>> bands = compute_bollinger_bands(prices, 5, 2)
    >>> round(bands["middle"], 2)
    3.0
    >>> round(bands["upper"], 2)
    6.16
    >>> round(bands["lower"], 2)
    -0.16
    """
    if len(prices) < period:
        raise DSLError(f"Not enough data to calculate Bollinger Bands with period {period}.")

    middle = compute_sma(prices, period)
    stddev = statistics.stdev(prices[-period:])
    upper = middle + multiplier * stddev
    lower = middle - multiplier * stddev

    return {"lower": lower, "middle": middle, "upper": upper}


def compute_ema_series(prices: list[float], period: int) -> list[float]:
    """

    Calcula a série da Média Móvel Exponencial (EMA) para uma lista de preços.

    Utiliza a média móvel simples dos primeiros ``period`` valores como ponto de partida e,
    em seguida, calcula a EMA para os valores subsequentes. Se a quantidade de preços for insuficiente,
    uma exceção DSLError é levantada.

    Parameters
    ----------
    prices : list of float
        Lista de preços.
    period : int
        Período para o cálculo da EMA.

    Returns
    -------
    list of float
        Lista contendo os valores da EMA calculados para cada preço após o período inicial.

    Raises
    ------
    DSLError
        Se o número de preços for insuficiente para o período solicitado.

    Examples
    --------
    >>> compute_ema_series([1, 2, 3, 4, 5], 3)
    [3.0, 4.0]
    """
    if len(prices) < period:
        raise DSLError(f"Not enough data to calculate EMA series with period {period}.")

    k = 2 / (period + 1)
    ema_series = []
    ema = compute_sma(prices[:period], period)  # Usa a média simples como primeiro valor

    for price in prices[period:]:
        ema = price * k + ema * (1 - k)
        ema_series.append(ema)

    return ema_series


def compute_macd(
    prices: list[float], fast: int = 12, slow: int = 26, signal: int = 9
) -> dict[str, float]:
    """
    Calcula o Moving Average Convergence Divergence (MACD) para uma lista de preços.

    O MACD é definido como a diferença entre duas EMAs com períodos diferentes (``fast`` e ``slow``).
    Em seguida, é calculada uma EMA da série MACD (denominada "signal") e o histograma é obtido
    subtraindo-se o valor do signal do último valor da série MACD. Se a quantidade de preços for
    insuficiente para os períodos solicitados ou para calcular a série do signal, uma exceção DSLError é levantada.

    Parameters
    ----------
    prices : list of float
        Lista de preços.
    fast : int, optional
        Período da EMA rápida. Valor padrão é 12.
    slow : int, optional
        Período da EMA lenta. Valor padrão é 26.
    signal : int, optional
        Período para o cálculo da EMA do MACD (signal). Valor padrão é 9.

    Returns
    -------
    dict of {str: float}
        Dicionário contendo as chaves:
            - "macd": último valor da série MACD.
            - "signal": último valor da série do signal.
            - "histogram": diferença entre "macd" e "signal".

    Raises
    ------
    DSLError
        Se o número de preços for insuficiente para os períodos solicitados ou para calcular a série do signal.

    Examples
    --------
    >>> prices = list(range(1, 10))
    >>> result = compute_macd(prices, fast=3, slow=5, signal=3)
    >>> result["macd"]
    1.0
    >>> result["signal"]
    1.0
    >>> result["histogram"]
    0.0
    """
    if len(prices) < slow:
        raise DSLError("Not enough data to calculate MACD.")

    ema_fast = compute_ema_series(prices, fast)
    ema_slow = compute_ema_series(prices, slow)
    macd_series = [f - s for f, s in zip(ema_fast[-len(ema_slow) :], ema_slow, strict=False)]

    macd_last = macd_series[-1]
    signal_series = compute_ema_series(macd_series, signal)
    signal_last = signal_series[-1]
    histogram = macd_last - signal_last

    return {"macd": macd_last, "signal": signal_last, "histogram": histogram}


def compute_rsi(prices: list[float], period: int = 14) -> float:
    """
    Calcula o Índice de Força Relativa (RSI) para uma lista de preços.

    O RSI é calculado com base nas variações de preços entre períodos consecutivos, comparando
    os ganhos médios e as perdas médias. Em uma tendência de alta contínua, o RSI tende a 100,
    enquanto em uma tendência de baixa, tende a 0. Se a quantidade de preços for insuficiente
    (menos de period + 1 valores), uma exceção DSLError é levantada.

    Parameters
    ----------
    prices : list of float
        Lista de preços.
    period : int, optional
        Período utilizado para o cálculo do RSI. Valor padrão é 14.

    Returns
    -------
    float
        Valor do RSI calculado, variando de 0 a 100.

    Raises
    ------
    DSLError
        Se o número de preços for insuficiente para o período solicitado.

    Examples
    --------
    >>> prices = list(range(1, 16))
    >>> compute_rsi(prices)
    100
    """
    if len(prices) < period + 1:
        raise DSLError("Not enough data to calculate RSI.")

    gains, losses = [], []
    for i in range(1, len(prices)):
        delta = prices[i] - prices[i - 1]
        gains.append(max(delta, 0))
        losses.append(abs(min(delta, 0)))

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    for i in range(period, len(prices) - 1):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))
