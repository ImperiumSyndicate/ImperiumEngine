import numpy as np
import pandas as pd
import pytest

from imperiumengine.indicators.atr import ATR


class TestATR:
    def test_calculate_atr(self) -> None:
        """Criação de um DataFrame de exemplo"""
        data = pd.DataFrame(
            {"high": [10, 12, 11, 13], "low": [5, 6, 7, 8], "close": [7, 10, 9, 11]}
        )

        # Instanciação do indicador ATR com period=2 (para facilitar os cálculos)
        atr_indicator = ATR(data, period=2)
        result = atr_indicator.calculate()

        # Valores esperados para o ATR, conforme os cálculos:
        expected = [5.0, 5.666666666666667, 4.555555555555556, 4.8518518518518515]

        # Verifica se os valores calculados estão próximos dos esperados
        np.testing.assert_allclose(result["ATR"].values, expected, rtol=1e-5, atol=1e-8)


if __name__ == "__main__":
    pytest.main([__file__])
