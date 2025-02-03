import numpy as np
import numpy.testing as npt
import pandas as pd
import pytest

from imperiumengine.indicators.rsi import RSI


class TestRSI:
    def test_calculate_rsi(self) -> None:
        """Cria um DataFrame de exemplo com a coluna 'close'"""
        data = pd.DataFrame({"close": [10, 12, 11, 13, 14]})

        # Instancia o indicador RSI com period=3 para facilitar os cálculos manuais
        rsi_indicator = RSI(data.copy(), price_column="close", period=3)
        result = rsi_indicator.calculate()

        # Valores esperados para o RSI, conforme os cálculos manuais:
        # Índice 0: 0.0
        # Índice 1: 100.0
        # Índice 2: 66.666667
        # Índice 3: 80.0
        # Índice 4: 75.0
        expected_rsi = np.array([0.0, 100.0, 66.666667, 80.0, 75.0])

        # Compara os valores calculados com os esperados
        npt.assert_allclose(result["RSI"].values, expected_rsi, rtol=1e-5, atol=1e-5)


if __name__ == "__main__":
    pytest.main([__file__])
