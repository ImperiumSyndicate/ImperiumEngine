import numpy.testing as npt
import pandas as pd
import pytest

from imperiumengine.indicators.ema import EMA


class TestEMA:
    def test_calculate_ema(self) -> None:
        """Cria um DataFrame simples com valores conhecidos"""
        data = pd.DataFrame({"Close": [1, 2, 3, 4]})

        # Usamos period=3. Neste caso, o fator alpha é 2/(3+1)=0.5.
        # Cálculos manuais com adjust=False (EMA recursivo):
        # EMA_0 = 1
        # EMA_1 = 2*0.5 + 1*(1-0.5) = 1 + 0.5 = 1.5
        # EMA_2 = 3*0.5 + 1.5*0.5 = 1.5 + 0.75 = 2.25
        # EMA_3 = 4*0.5 + 2.25*0.5 = 2 + 1.125 = 3.125
        expected_ema = [1, 1.5, 2.25, 3.125]

        # Instancia o indicador EMA
        ema_indicator = EMA(data.copy(), period=3, price_column="Close")
        result = ema_indicator.calculate()

        # Verifica se a coluna "EMA_3" existe e se os valores são os esperados
        ema_col = f"EMA_{3}"
        npt.assert_allclose(result[ema_col].values, expected_ema, rtol=1e-5, atol=1e-8)


if __name__ == "__main__":
    pytest.main([__file__])
