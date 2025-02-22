import numpy as np
import pandas as pd

from imperiumengine.indicators.macd import MACD

if __name__ == "__main__":
    # Cria um gerador de números aleatórios para reprodutibilidade
    rng = np.random.default_rng(42)
    dates = pd.date_range(start="2023-01-01", periods=100, freq="D")
    prices = rng.lognormal(mean=0, sigma=0.1, size=100).cumprod() * 100

    # Cria um DataFrame com os preços gerados.
    df = pd.DataFrame({"Close": prices}, index=dates)

    # Instancia o indicador MACD, especificando que a coluna de preço é "Close"
    macd = MACD(data=df, short_period=12, long_period=26, signal_period=9, price_column="Close")

    # Calcula o MACD e atualiza o DataFrame
    result = macd.calculate()

    # Exibe as 25 primeiras linhas do DataFrame resultante
    print(result.head(25))
