import pandas as pd

from imperiumengine.indicators.vwap import VWAP

if __name__ == "__main__":
    # Cria dados de exemplo
    dates = pd.date_range(start="2023-01-01", periods=10, freq="D")
    # Simula preços de fechamento e volumes (valores fictícios)
    data = {
        "close": [105.0, 107.5, 103.0, 110.0, 108.0, 112.0, 115.0, 113.0, 118.0, 116.0],
        "volume": [1000, 1500, 1200, 1300, 1600, 1800, 1700, 1400, 1900, 2000],
    }
    df = pd.DataFrame(data, index=dates)

    # Instancia o indicador VWAP (assegure-se de que o DataFrame contenha as colunas 'close' e 'volume')
    vwap_indicator = VWAP(data=df)

    # Calcula o VWAP e atualiza o DataFrame
    result = vwap_indicator.calculate()

    # Exibe o DataFrame resultante
    print(result)
