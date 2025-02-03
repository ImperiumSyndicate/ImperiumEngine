import numpy as np
import pandas as pd

from imperiumengine.indicators.base_indicator import FinancialIndicator


class VWAP(FinancialIndicator):
    """
    Volume Weighted Average Price (VWAP).

    O VWAP é um indicador técnico que calcula o preço médio ponderado pelo volume
    de um ativo durante um determinado período.

    Métodos
    -------
    calculate() -> pd.DataFrame
        Calcula o VWAP com base nos dados de fechamento e volume.

    Atributos
    ---------
    self.data : pandas.DataFrame
        DataFrame contendo os preços de fechamento e volume do ativo.
    """

    def calculate(self) -> pd.DataFrame:
        """
        Calcula o VWAP (Volume Weighted Average Price).

        Retorna
        -------
        pd.DataFrame
            DataFrame atualizado com uma nova coluna 'VWAP', contendo os valores calculados.

        Exemplos
        --------
        >>> import pandas as pd
        >>> from imperiumengine.indicators.vwap import VWAP
        >>> # Criação de um DataFrame de exemplo com colunas 'close' e 'volume'
        >>> data = pd.DataFrame({"close": [10, 20, 30, 40], "volume": [100, 200, 300, 400]})
        >>> vwap_indicator = VWAP(data)
        >>> result = vwap_indicator.calculate()
        >>> result["VWAP"].tolist()
        [10.0, 16.666666666666668, 23.333333333333332, 30.0]
        """
        cum_volume = self.data["volume"].cumsum()
        cum_vwap = (self.data["close"] * self.data["volume"]).cumsum()
        self.data["VWAP"] = np.where(cum_volume == 0, np.nan, cum_vwap / cum_volume)
        self.log("VWAP calculado com sucesso.")
        return self.data
