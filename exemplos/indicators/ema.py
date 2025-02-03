import numpy as np
import pandas as pd

from imperiumengine.indicators.ema import EMA

if __name__ == "__main__":
    # Cria um gerador de números aleatórios para reprodutibilidade
    rng = np.random.default_rng(420)
    dates = pd.date_range(start="2023-01-01", periods=100, freq="D")
    prices = rng.lognormal(mean=0, sigma=0.1, size=100).cumprod() * 100

    # Cria um DataFrame com os preços gerados.
    # Certifique-se de que o nome da coluna está correto.
    df = pd.DataFrame({"Close": prices}, index=dates)

    # Instancia o indicador EMA, especificando que a coluna de preço é "Close"
    ema = EMA(data=df, period=14, price_column="Close")

    # Calcula a EMA e atualiza o DataFrame
    result = ema.calculate()

    # Exibe as 20 primeiras linhas do DataFrame resultante
    print(result.head(20))
