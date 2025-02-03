import numpy as np
import numpy.testing as npt
import pandas as pd
import pytest

from imperiumengine.indicators.vwap import VWAP


class TestVWAP:
    def test_calculate_vwap(self) -> None:
        """Cria um DataFrame de exemplo com as colunas 'close' e 'volume'"""
        data = pd.DataFrame({"close": [10, 20, 30, 40], "volume": [100, 200, 300, 400]})

        # Instancia o indicador VWAP
        vwap_indicator = VWAP(data)

        # Calcula o VWAP
        result = vwap_indicator.calculate()

        # Valores esperados:
        # Cumulative volume: [100, 300, 600, 1000]
        # Cumulative weighted sum: [10*100, 10*100 + 20*200, 10*100 + 20*200 + 30*300, 10*100 + 20*200 + 30*300 + 40*400]
        #   = [1000, 5000, 14000, 30000]
        # VWAP = [1000/100, 5000/300, 14000/600, 30000/1000] = [10.0, 16.666666666666668, 23.333333333333332, 30.0]
        expected_vwap = np.array([10.0, 16.666666666666668, 23.333333333333332, 30.0])

        # Compara os valores calculados com os valores esperados
        npt.assert_allclose(result["VWAP"].values, expected_vwap, rtol=1e-5, atol=1e-8)


if __name__ == "__main__":
    pytest.main([__file__])
