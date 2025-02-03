import pandas as pd

from imperiumengine.indicators.atr import ATR

if __name__ == "__main__":
    # Exemplo de uso
    data = pd.DataFrame(
        {
            "close": [100, 102, 101, 105, 107],
            "volume": [200, 220, 250, 230, 210],
            "high": [101, 103, 102, 106, 108],
            "low": [99, 101, 100, 104, 106],
        }
    )

    atr_indicator = ATR(data)
    result_atr = atr_indicator.calculate()
    print(result_atr)
