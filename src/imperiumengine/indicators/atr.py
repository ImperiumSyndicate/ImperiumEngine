import numpy as np
import pandas as pd

from imperiumengine.indicators.base_indicator import FinancialIndicator


class ATR(FinancialIndicator):
    """
    Average True Range (ATR).

    O ATR é um indicador técnico que mede a volatilidade de um ativo ao calcular
    a média móvel exponencial da amplitude real dos preços.

    Parâmetros
    ----------
    data : pandas.DataFrame
        DataFrame contendo as colunas 'high', 'low' e 'close'.
    period : int, opcional, padrão=14
        Período utilizado para calcular a média móvel exponencial.

    Métodos
    -------
    calculate() -> pandas.DataFrame
        Calcula o ATR com base nos dados de alta, baixa e fechamento.
    """

    def __init__(self, data: pd.DataFrame, period: int = 14) -> None:
        super().__init__(data)
        self.period: int = period

    def calculate(self) -> pd.DataFrame:
        """
        Calcula o ATR (Average True Range).

        Retorna
        -------
        pandas.DataFrame
            DataFrame atualizado com uma nova coluna 'ATR', contendo os valores calculados.

        Exemplos
        --------
        Neste exemplo, utilizamos um DataFrame simples e definimos `period=2`
        para facilitar o acompanhamento dos cálculos do ATR.

        Considere o seguinte DataFrame de exemplo:

        >>> import pandas as pd
        >>> from imperiumengine.indicators.atr import ATR
        >>> data = pd.DataFrame(
        ...     {"high": [10, 12, 11, 13], "low": [5, 6, 7, 8], "close": [7, 10, 9, 11]}
        ... )
        >>> # Usamos period=2, onde o fator de suavização alpha = 2/(2+1) = 2/3.
        >>> # Cálculo do True Range (TR):
        >>> # Linha 0: TR = high - low = 10 - 5 = 5
        >>> # Linha 1: TR = max(12-6, |12-7|, |6-7|) = max(6, 5, 1) = 6
        >>> # Linha 2: TR = max(11-7, |11-10|, |7-10|) = max(4, 1, 3) = 4
        >>> # Linha 3: TR = max(13-8, |13-9|, |8-9|) = max(5, 4, 1) = 5
        >>>
        >>> # Cálculo do ATR usando EWMA:
        >>> # Linha 0: ATR_0 = 5
        >>> # Linha 1: ATR_1 = 6*(2/3) + 5*(1/3) = 5.666666666666667
        >>> # Linha 2: ATR_2 = 4*(2/3) + ATR_1*(1/3) = 4.555555555555556
        >>> # Linha 3: ATR_3 = 5*(2/3) + ATR_2*(1/3) = 4.8518518518518515
        >>>
        >>> atr_indicator = ATR(data, period=2)
        >>> result = atr_indicator.calculate()
        >>> result["ATR"].tolist()
        [5.0, 5.666666666666667, 4.55555555555555..., 4.85185185185185...]
        """
        # Cálculo do True Range (TR)
        high_low = self.data["high"] - self.data["low"]
        # Preenche os NaN resultantes do shift com 0 para que o cálculo na primeira linha use apenas high - low
        high_close = np.abs(self.data["high"] - self.data["close"].shift()).fillna(0)
        low_close = np.abs(self.data["low"] - self.data["close"].shift()).fillna(0)
        tr = np.maximum.reduce([high_low, high_close, low_close])

        # Calcula a média móvel exponencial do TR para obter o ATR
        self.data["ATR"] = (
            pd.Series(tr, index=self.data.index).ewm(span=self.period, adjust=False).mean()
        )
        self.log("ATR calculado com sucesso.")
        return self.data
