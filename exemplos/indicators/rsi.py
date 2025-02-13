import numpy as np
import pandas as pd

from imperiumengine.indicators.rsi import RSI

if __name__ == "__main__":
    # Cria um gerador de números aleatórios com seed para reprodutibilidade
    rng = np.random.default_rng(42)
    dates = pd.date_range(start="2023-01-01", periods=100, freq="D")
    prices = rng.lognormal(mean=0, sigma=0.1, size=100).cumprod() * 100

    # Cria um DataFrame com os preços gerados.
    # Atenção: o nome da coluna deve corresponder ao parâmetro price_column, aqui 'close'
    df = pd.DataFrame({"close": prices}, index=dates)

    # Instancia o indicador RSI
    rsi_indicator = RSI(data=df, price_column="close", period=14)

    # Calcula o RSI e atualiza o DataFrame
    result = rsi_indicator.calculate()

    # Exibe as 20 primeiras linhas do DataFrame resultante
    print(result.head(20))
