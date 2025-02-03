import pandas as pd

from imperiumengine.indicators.base_indicator import FinancialIndicator


class BollingerBands(FinancialIndicator):
    """
    Indicador das Bandas de Bollinger.

    Calcula a Média Móvel Simples (SMA) e utiliza-a, juntamente com o desvio padrão, para
    calcular as bandas superior e inferior de Bollinger. Os cálculos são realizados utilizando
    uma janela móvel.

    As fórmulas utilizadas são:

    - **SMA**: média móvel dos preços sobre o período especificado.
    - **Desvio Padrão (std)**: desvio padrão dos preços sobre o mesmo período.
    - **Banda Superior**: SMA + (std_dev * std)
    - **Banda Inferior**: SMA - (std_dev * std)

    Parâmetros
    ----------
    data : pd.DataFrame
        DataFrame contendo os dados financeiros. Deve incluir uma coluna especificada por `price_column`.
    period : int, opcional
        Número de períodos a serem usados para o cálculo da SMA e do desvio padrão. Padrão é 20.
    std_dev : int ou float, opcional
        Multiplicador para o desvio padrão utilizado no cálculo das bandas. Padrão é 2.
    price_column : str, opcional
        Nome da coluna que contém os dados de preço. Padrão é 'Close'.

    Atributos
    ---------
    period : int
        Período utilizado para os cálculos móveis.
    std_dev : int ou float
        Multiplicador do desvio padrão.

    Métodos
    -------
    calculate() -> pd.DataFrame
        Calcula a SMA, a Banda Superior e a Banda Inferior e retorna o DataFrame com as bandas adicionadas.

    Exemplos
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> dates = pd.date_range("2023-01-01", periods=100, freq="D")
    >>> prices = np.random.lognormal(mean=0, sigma=0.1, size=100).cumprod() * 100
    >>> df = pd.DataFrame({"Close": prices}, index=dates)
    >>> bb = BollingerBands(data=df, period=20, std_dev=2, price_column="Close")
    >>> result = bb.calculate()
    """

    def __init__(
        self, data: pd.DataFrame, period: int = 20, std_dev: float = 2, price_column: str = "Close"
    ) -> None:
        super().__init__(data, price_column)
        self.period: int = period
        self.std_dev: int | float = std_dev

    def calculate(self) -> pd.DataFrame:
        """
        Calcula as Bandas de Bollinger.

        Realiza o cálculo da média móvel simples (SMA) e do desvio padrão para o período especificado,
        e a partir destes valores, calcula as bandas superior e inferior.

        Retorna
        -------
        pd.DataFrame
            DataFrame com duas novas colunas:

            - 'Upper_Band': A banda superior de Bollinger.
            - 'Lower_Band': A banda inferior de Bollinger.
        """
        sma = self.data[self.price_column].rolling(window=self.period).mean()
        std = self.data[self.price_column].rolling(window=self.period).std()
        self.data["Upper_Band"] = sma + (std * self.std_dev)
        self.data["Lower_Band"] = sma - (std * self.std_dev)
        self.log("Bollinger Bands calculated successfully.")
        return self.data
