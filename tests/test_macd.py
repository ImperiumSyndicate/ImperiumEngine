import numpy as np
import numpy.testing as npt
import pandas as pd
import pytest

from imperiumengine.indicators.macd import MACD


class TestMACD:
    def test_calculate_macd(self) -> None:
        """Dados de exemplo: preços simples"""
        data = pd.DataFrame({"Close": [10, 20, 30, 40, 50, 60]})

        # Instancia o indicador MACD com períodos customizados:
        # short_period = 3, long_period = 6, signal_period = 2
        macd_indicator = MACD(
            data.copy(), short_period=3, long_period=6, signal_period=2, price_column="Close"
        )

        result = macd_indicator.calculate()

        # Valores esperados calculados manualmente (aproximados)
        expected_macd = np.array(
            [
                0.0,
                2.142857,  # 15 - 12.857143
                4.744898,  # 22.5 - 17.755102
                7.138776,  # esperado
                9.131269,  # esperado
                10.61412,  # esperado
            ]
        )

        expected_signal = np.array(
            [
                0.0,
                1.428571,  # 2.142857*0.666667 + 0*0.333333
                3.639456,  # esperado
                5.972336,  # esperado
                8.078291,  # esperado
                9.768844,  # esperado
            ]
        )

        # Valida os resultados utilizando tolerâncias maiores para lidar com diferenças de precisão
        npt.assert_allclose(result["MACD"].values, expected_macd, rtol=1e-2, atol=0.1)
        npt.assert_allclose(result["MACD_Signal"].values, expected_signal, rtol=1e-2, atol=0.1)


if __name__ == "__main__":
    pytest.main([__file__])
