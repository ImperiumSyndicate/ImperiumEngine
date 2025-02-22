from typing import Any

from imperiumengine.config.logger import LogFactory
from imperiumengine.dsl.context import Context
from imperiumengine.dsl.exceptions import DSLError
from imperiumengine.dsl.utils import (
    compute_atr,
    compute_bollinger_bands,
    compute_ema,
    compute_macd,
    compute_rsi,
    compute_sma,
)


class IndicatorInstruction:
    """
    Calcula um indicador de mercado a partir dos dados fornecidos.

    Esta classe realiza o cálculo de um indicador de mercado com base nos parâmetros
    presentes em um dicionário (`indicator_data`). Os indicadores suportados incluem:
    "SMA", "EMA", "ATR", "BollingerBands", "MACD" e "RSI". Para cada indicador, é
    possível configurar parâmetros específicos, como período, fonte dos preços e outros
    valores necessários para o cálculo (por exemplo, "fast", "slow" e "signal" para o MACD).

    Parâmetros
    ----------
    indicator_data : dict
        Dicionário contendo os parâmetros necessários para o cálculo do indicador.
        Parâmetros esperados:
          - "name" : str
                Nome do indicador a ser calculado. Valores possíveis: "SMA", "EMA", "ATR",
                "BollingerBands", "MACD", "RSI".
          - "period" : int, opcional
                Período utilizado no cálculo do indicador (valor padrão é 14).
          - "source" : str, opcional
                Nome da variável no contexto que contém os preços (valor padrão "close").
          - "var" : str
                Nome da variável onde o resultado do indicador será armazenado no contexto.
          - Outros parâmetros específicos, como:
                * "multiplier" para BollingerBands;
                * "fast", "slow" e "signal" para MACD.

    Atributos
    ---------
    indicator_data : dict
        Armazena os parâmetros do indicador.
    logger : logging.Logger
        Logger utilizado para registrar informações, debug e erros durante a execução.

    Métodos
    -------
    _compute_indicator(name: str, prices: list[float], context: Context) -> Any
        Calcula o valor do indicador com base no nome, na lista de preços e no contexto.
    _get_required_param(param_name: str) -> Any
        Recupera um parâmetro obrigatório do dicionário `indicator_data`.
    execute(context: Context) -> None
        Executa o cálculo do indicador e armazena o resultado no contexto.

    Exemplos
    --------
    >>> from imperiumengine.dsl.context import Context
    >>> # Exemplo de configuração para cálculo de SMA com período 3 (dados suficientes para o cálculo)
    >>> dados = {"name": "SMA", "period": 3, "source": "close", "var": "sma_result"}
    >>> indicador = IndicatorInstruction(dados)
    >>> # Supondo que o contexto possua a lista de preços na variável "close"
    >>> contexto = Context()
    >>> contexto.variables["close"] = [10, 12, 11, 13, 12, 14]
    >>> indicador.execute(contexto)
    >>> # O resultado do cálculo estará armazenado em contexto.variables["sma_result"]
    >>> contexto.variables["sma_result"]
    13.0
    """

    def __init__(self, indicator_data: dict) -> None:
        """
        Inicializa a instrução de indicador com os dados fornecidos.

        Parameters
        ----------
        indicator_data : dict
            Dicionário contendo os parâmetros necessários para o cálculo do indicador.
        """
        self.indicator_data = indicator_data
        self.logger = LogFactory.get_logger(self.__class__.__name__)
        self.logger.info("IndicatorInstruction instance created with data: %s", self.indicator_data)

    def _compute_indicator(self, name: str, prices: list[float], context: Context) -> Any:
        """
        Calcula o indicador de mercado especificado.

        Seleciona e executa a função de cálculo apropriada para o indicador identificado por
        `name`, utilizando os preços fornecidos e os parâmetros presentes em `indicator_data`.
        Para o indicador "MACD", parâmetros adicionais ("fast", "slow" e "signal") são
        obrigatórios.

        Parameters
        ----------
        name : str
            Nome do indicador a ser calculado. Exemplos: "SMA", "EMA", "ATR", "BollingerBands",
            "MACD", "RSI".
        prices : list of float
            Lista de preços utilizada no cálculo do indicador.
        context : Context
            Objeto que pode fornecer variáveis adicionais necessárias, como as listas "high", "low"
            e "close" para o cálculo do ATR.

        Returns
        -------
        Any
            Valor calculado do indicador. O tipo do retorno pode variar conforme o indicador.

        Raises
        ------
        DSLError
            Se o indicador não for suportado ou ocorrer algum erro durante o cálculo.
        """
        self.logger.debug("Computing indicator: %s with data: %s", name, self.indicator_data)

        try:
            if name == "SMA":
                result = compute_sma(prices, int(self.indicator_data.get("period", 14)))
            elif name == "EMA":
                result = compute_ema(prices, int(self.indicator_data.get("period", 14)))
            elif name == "ATR":
                highs = context.variables.get("high", [])
                lows = context.variables.get("low", [])
                closes = context.variables.get("close", [])
                result = compute_atr(
                    highs, lows, closes, int(self.indicator_data.get("period", 14))
                )
            elif name == "BollingerBands":
                multiplier = float(self.indicator_data.get("multiplier", 2))
                result = compute_bollinger_bands(
                    prices, int(self.indicator_data.get("period", 14)), multiplier
                )
            elif name == "MACD":
                fast = int(self._get_required_param("fast"))
                slow = int(self._get_required_param("slow"))
                signal = int(self._get_required_param("signal"))
                result = compute_macd(prices, fast, slow, signal)
            elif name == "RSI":
                result = compute_rsi(prices, int(self.indicator_data.get("period", 14)))
            else:
                raise DSLError(f"Indicator '{name}' not supported.")

            self.logger.debug("Computed %s: %s", name, result)
            return result

        except DSLError as e:
            self.logger.error("Error computing indicator '%s': %s", name, str(e))
            raise
        except Exception as e:
            self.logger.exception("Unexpected error computing indicator '%s'", name)
            raise DSLError(f"Unexpected error computing {name}: {e}")

    def _get_required_param(self, param_name: str) -> Any:
        """
        Recupera um parâmetro obrigatório do dicionário `indicator_data`.

        Verifica se o parâmetro especificado existe em `indicator_data`. Caso não exista,
        registra um erro e levanta uma exceção `DSLError`.

        Parameters
        ----------
        param_name : str
            Nome do parâmetro a ser recuperado.

        Returns
        -------
        Any
            Valor associado ao parâmetro requisitado.

        Raises
        ------
        DSLError
            Se o parâmetro não estiver presente em `indicator_data`.
        """
        value = self.indicator_data.get(param_name)
        if value is None:
            self.logger.error("Missing required parameter: '%s'", param_name)
            raise DSLError(f"Missing '{param_name}' value in indicator data.")
        return value

    def execute(self, context: Context) -> None:
        """
        Executa o cálculo do indicador e armazena o resultado no contexto.

        Recupera os parâmetros obrigatórios ("name" e "var") e, opcionalmente, o parâmetro "source"
        (com valor padrão "close"). Em seguida, extrai a lista de preços do contexto e realiza o
        cálculo do indicador por meio do método `_compute_indicator`. O resultado é armazenado em
        `context.variables` utilizando o nome da variável especificado.

        Parameters
        ----------
        context : Context
            Objeto que contém as variáveis e o estado de execução. É esperado que contenha os dados
            (por exemplo, preços) necessários para o cálculo do indicador.

        Raises
        ------
        DSLError
            Se ocorrer algum erro na execução do cálculo do indicador.

        """
        try:
            name = self._get_required_param("name")
            source = self.indicator_data.get("source", "close")
            var_name = self._get_required_param("var")

            self.logger.debug(
                "Executing indicator '%s' with source '%s' and var '%s'", name, source, var_name
            )

            prices = context.variables.get(source, [])
            value = self._compute_indicator(name, prices, context)

            context.variables[var_name] = value

            period = self.indicator_data.get("period", 14) if name != "MACD" else "N/A"
            self.logger.info("Indicator %s (period %s) calculated: %s", name, period, value)

        except DSLError as e:
            self.logger.error("Execution failed: %s", str(e))
            raise
        except Exception as e:
            self.logger.exception("Unexpected error during execution")
            raise DSLError(f"Unexpected error during execution: {e}")
