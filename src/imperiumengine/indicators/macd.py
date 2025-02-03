from typing import Any, cast

import pandas as pd

from imperiumengine.indicators.base_indicator import FinancialIndicator


class MACD(FinancialIndicator):
    """
    Convergência/Divergência da Média Móvel (MACD).

    Calcula o indicador MACD a partir dos preços utilizando as médias móveis exponenciais (EMAs)
    de períodos curto e longo e gera uma linha de sinal a partir da EMA do MACD.

    Parâmetros
    ----------
    data : pd.DataFrame
        DataFrame contendo os dados financeiros. Deve incluir a coluna definida por `price_column`.
    short_period : int, opcional
        Número de períodos para calcular a EMA de curto prazo. Padrão é 12.
    long_period : int, opcional
        Número de períodos para calcular a EMA de longo prazo. Padrão é 26.
    signal_period : int, opcional
        Número de períodos para calcular a linha de sinal (EMA do MACD). Padrão é 9.
    price_column : str, opcional
        Nome da coluna que contém os dados de preço. Padrão é 'Close'.

    Atributos
    ---------
    short_period : int
        Número de períodos para a EMA de curto prazo.
    long_period : int
        Número de períodos para a EMA de longo prazo.
    signal_period : int
        Número de períodos para a linha de sinal.

    Métodos
    -------
    calculate() -> pd.DataFrame
        Calcula o MACD e a linha de sinal, adicionando duas novas colunas ao DataFrame: 'MACD' e 'MACD_Signal'.

    Exemplos
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> dates = pd.date_range("2023-01-01", periods=100, freq="D")
    >>> prices = np.random.lognormal(mean=0, sigma=0.1, size=100).cumprod() * 100
    >>> df = pd.DataFrame({"Close": prices}, index=dates)
    >>> macd = MACD(data=df, short_period=12, long_period=26, signal_period=9, price_column="Close")
    >>> result = macd.calculate()
    """

    def __init__(
        self,
        data: pd.DataFrame,
        short_period: int = 12,
        long_period: int = 26,
        signal_period: int = 9,
        price_column: str = "Close",
    ) -> None:
        super().__init__(data, price_column)
        self.short_period: int = short_period
        self.long_period: int = long_period
        self.signal_period: int = signal_period

    def calculate(self) -> pd.DataFrame:
        """
        Calcula o indicador MACD e a linha de sinal.

        Calcula a EMA de curto prazo e a EMA de longo prazo para os preços, subtrai as duas para obter o MACD,
        e então calcula a linha de sinal como a EMA do MACD.

        Retorna
        -------
        pd.DataFrame
            DataFrame com duas novas colunas:
            - 'MACD': O valor do MACD.
            - 'MACD_Signal': A linha de sinal derivada do MACD.
        """
        short_ema: pd.Series = (
            self.data[self.price_column].ewm(span=self.short_period, adjust=False).mean()
        )
        long_ema: pd.Series = (
            self.data[self.price_column].ewm(span=self.long_period, adjust=False).mean()
        )
        self.data["MACD"] = short_ema - long_ema
        self.data["MACD_Signal"] = (
            self.data["MACD"].ewm(span=self.signal_period, adjust=False).mean()
        )
        # Use cast to Any to bypass type-checking for the untyped 'log' method.
        cast(Any, self.log)("MACD calculado com sucesso.")
        return self.data
