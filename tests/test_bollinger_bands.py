import numpy as np
import pandas as pd
import pytest

from imperiumengine.indicators.bollinger_bands import BollingerBands


class TestBollingerBands:
    def test_calculate_bollinger_bands(self) -> None:
        """Dados de exemplo"""
        data = pd.DataFrame({"Close": [10, 20, 30, 40, 50]})

        # Usamos period=3 para facilitar o cálculo:
        # Para os primeiros 2 valores, o rolling não possui dados suficientes e retorna NaN.
        # Para o índice 2, a janela é [10, 20, 30]:
        #   - SMA = (10+20+30)/3 = 20
        #   - std = sqrt(((10-20)^2 + (20-20)^2 + (30-20)^2) / (3-1))
        #         = sqrt((100+0+100)/2) = sqrt(200/2) = sqrt(100) = 10
        #   - Upper_Band = 20 + 2*10 = 40
        #   - Lower_Band = 20 - 2*10 = 0
        #
        # Para os índices 3 e 4, os cálculos seguem de forma análoga:
        # Índice 3 (janela: [20,30,40]): SMA = 30, std = 10, Upper_Band = 30 + 20 = 50, Lower_Band = 30 - 20 = 10
        # Índice 4 (janela: [30,40,50]): SMA = 40, std = 10, Upper_Band = 40 + 20 = 60, Lower_Band = 40 - 20 = 20

        # Instancia o indicador com period=3 e std_dev=2
        bb = BollingerBands(data, period=3, std_dev=2, price_column="Close")
        result = bb.calculate()

        # Valores esperados para as bandas (os dois primeiros índices serão NaN)
        expected_upper = [np.nan, np.nan, 40, 50, 60]
        expected_lower = [np.nan, np.nan, 0, 10, 20]

        # Verifica se os valores calculados estão próximos dos esperados
        np.testing.assert_allclose(
            result["Upper_Band"].values,
            np.array(expected_upper),
            rtol=1e-5,
            atol=1e-8,
            equal_nan=True,
        )
        np.testing.assert_allclose(
            result["Lower_Band"].values,
            np.array(expected_lower),
            rtol=1e-5,
            atol=1e-8,
            equal_nan=True,
        )


if __name__ == "__main__":
    pytest.main([__file__])
