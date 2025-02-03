import logging
from pathlib import Path

import pandas as pd


class FinancialIndicator:
    """Classe base para cálculo de indicadores financeiros."""

    def __init__(self, data: pd.DataFrame, price_column: str = "close") -> None:
        self.data: pd.DataFrame = data
        self.price_column: str = price_column
        self.logger: logging.Logger | None = None  # Inicializa o logger como None
        self.setup_logger()

    def setup_logger(self) -> None:
        """Configura um logger para cada indicador."""
        if self.logger is not None:
            return  # Evita reconfiguração do logger

        log_dir = Path(f"logs/indicators/{self.__class__.__name__}")
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"{self.__class__.__name__}.log"

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

        if not self.logger.hasHandlers():
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log(self, message: str) -> None:
        """Método para registrar mensagens no log."""
        if self.logger:
            self.logger.info(message)

    def calculate(self) -> None:
        """
        Método a ser implementado pelas classes filhas para calcular o indicador.

        Raises
        ------
        NotImplementedError
            Sempre, pois deve ser implementado na classe derivada.

        Exemplos
        --------
        >>> import pandas as pd
        >>> from imperiumengine.indicators.base_indicator import FinancialIndicator
        >>> df = pd.DataFrame({"close": [1, 2, 3]})
        >>> indicador = FinancialIndicator(df)
        >>> indicador.calculate()  # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        NotImplementedError: Método calculate() deve ser implementado na classe derivada
        """
        error_message = "Método calculate() deve ser implementado na classe derivada"
        raise NotImplementedError(error_message)
