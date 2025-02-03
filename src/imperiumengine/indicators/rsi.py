from typing import Any, cast

import numpy as np
import pandas as pd

from imperiumengine.indicators.base_indicator import FinancialIndicator


class RSI(FinancialIndicator):
    """
    Índice de Força Relativa (RSI).

    Calcula o RSI a partir dos dados de preços utilizando a variação dos preços e uma média móvel
    para ganhos e perdas.

    Parâmetros
    ----------
    data : pd.DataFrame
        DataFrame contendo os dados financeiros. Deve incluir a coluna definida por `price_column`.
    price_column : str, opcional
        Nome da coluna que contém os dados de preço. Padrão é 'close'.
    period : int, opcional
        Número de períodos para o cálculo do RSI. Padrão é 14.

    Atributos
    ---------
    period : int
        Período utilizado para o cálculo do RSI.

    Métodos
    -------
    calculate() -> pd.DataFrame
        Calcula o RSI e adiciona uma nova coluna 'RSI' ao DataFrame.

    Exemplos
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> dates = pd.date_range("2023-01-01", periods=100, freq="D")
    >>> prices = np.random.lognormal(mean=0, sigma=0.1, size=100).cumprod() * 100
    >>> df = pd.DataFrame({"close": prices}, index=dates)
    >>> rsi_indicator = RSI(data=df, price_column="close", period=14)
    >>> result = rsi_indicator.calculate()
    """

    def __init__(self, data: pd.DataFrame, price_column: str = "close", period: int = 14) -> None:
        super().__init__(data, price_column)
        self.period: int = period

    def calculate(self) -> pd.DataFrame:
        """
        Calcula o Índice de Força Relativa (RSI).

        Utiliza a variação dos preços para calcular os ganhos e perdas, em seguida calcula a média
        móvel dos ganhos e perdas e, a partir destes valores, determina o RSI.

        Retorna
        -------
        pd.DataFrame
            DataFrame com uma nova coluna 'RSI' contendo os valores do RSI.
        """
        # Calcula a variação dos preços
        delta: pd.Series = self.data[self.price_column].diff()

        # Se delta > 0, é ganho; caso contrário, zero.
        gain = np.where(delta > 0, delta, 0)
        # Se delta < 0, é perda (valor absoluto); caso contrário, zero.
        loss = np.where(delta < 0, -delta, 0)

        # Cria as séries garantindo que o índice seja o mesmo do DataFrame original
        gain_series: pd.Series = pd.Series(gain, index=self.data.index)
        loss_series: pd.Series = pd.Series(loss, index=self.data.index)

        # Calcula a média móvel dos ganhos e perdas
        avg_gain: pd.Series = gain_series.rolling(window=self.period, min_periods=1).mean()
        avg_loss: pd.Series = loss_series.rolling(window=self.period, min_periods=1).mean()

        # Evita divisão por zero: substitui zeros em avg_loss por NaN
        avg_loss = avg_loss.replace(0, np.nan)
        # Calcula a razão (RS) entre o ganho médio e a perda média
        rs: pd.Series = avg_gain / avg_loss.fillna(1e-10)
        # Calcula o RSI
        rsi: pd.Series = 100 - (100 / (1 + rs))

        self.data["RSI"] = rsi
        # Use cast to Any to bypass type-checking for the untyped 'log' method.
        cast(Any, self.log)("RSI calculado com sucesso.")
        return self.data
