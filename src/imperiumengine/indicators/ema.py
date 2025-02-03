import pandas as pd

from imperiumengine.indicators.base_indicator import FinancialIndicator


class EMA(FinancialIndicator):
    """
    Média Móvel Exponencial (EMA).

    Calcula a Média Móvel Exponencial (EMA) dos preços utilizando o período especificado.

    Parâmetros
    ----------
    data : pd.DataFrame
        DataFrame contendo os dados financeiros. Deve incluir a coluna definida por `price_column`.
    period : int, opcional
        Número de períodos para calcular a EMA. Padrão é 14.
    price_column : str, opcional
        Nome da coluna que contém os dados de preço. Padrão é 'Close'.

    Atributos
    ---------
    period : int
        Período utilizado para o cálculo da EMA.

    Métodos
    -------
    calculate()
        Calcula a EMA e adiciona uma nova coluna ao DataFrame com os resultados.

    Exemplos
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> dates = pd.date_range("2023-01-01", periods=100, freq="D")
    >>> prices = np.random.lognormal(mean=0, sigma=0.1, size=100).cumprod() * 100
    >>> df = pd.DataFrame({"Close": prices}, index=dates)
    >>> ema = EMA(data=df, period=14, price_column="Close")
    >>> result = ema.calculate()
    """

    def __init__(self, data: pd.DataFrame, period: int = 14, price_column: str = "Close") -> None:
        # Passa o parâmetro price_column para a classe base
        super().__init__(data, price_column)
        self.period: int = period

    def calculate(self) -> pd.DataFrame:
        """
        Calcula a Média Móvel Exponencial (EMA).

        Calcula a EMA dos preços utilizando o período especificado e adiciona uma nova coluna no DataFrame.

        Retorna
        -------
        pd.DataFrame
            DataFrame com uma nova coluna contendo a EMA calculada.
        """
        self.data[f"EMA_{self.period}"] = (
            self.data[self.price_column].ewm(span=self.period, adjust=False).mean()
        )
        self.log("EMA calculado com sucesso.")
        return self.data
