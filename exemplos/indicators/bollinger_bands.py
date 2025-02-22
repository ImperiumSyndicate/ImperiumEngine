import numpy as np
import pandas as pd

from imperiumengine.indicators.bollinger_bands import BollingerBands

if __name__ == "__main__":
    # Cria um gerador de números aleatórios para reprodutibilidade
    rng = np.random.default_rng(42)
    dates = pd.date_range(start="2023-01-01", periods=100, freq="D")
    prices = rng.lognormal(mean=0, sigma=0.1, size=100).cumprod() * 100

    df = pd.DataFrame({"Close": prices}, index=dates)
    bb = BollingerBands(data=df, period=20, std_dev=2, price_column="Close")
    result = bb.calculate()
    print(result.head(25))
