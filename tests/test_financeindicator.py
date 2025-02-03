import pandas as pd
import pytest

from imperiumengine.indicators.base_indicator import FinancialIndicator


class TestFinancialIndicator:
    def test_calculate_not_implemented(self) -> None:
        """Cria um DataFrame simples para testar"""
        df = pd.DataFrame({"close": [1, 2, 3]})
        indicador = FinancialIndicator(df)

        # Verifica se a chamada a calculate() lança o NotImplementedError
        with pytest.raises(NotImplementedError) as exc_info:
            indicador.calculate()
        expected_message = "Método calculate() deve ser implementado na classe derivada"
        assert expected_message in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__])
