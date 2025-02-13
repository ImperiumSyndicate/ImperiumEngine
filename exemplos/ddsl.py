import json
import time
from pathlib import Path

import requests
from binance.client import Client

from imperiumengine.config.logger import LogFactory
from imperiumengine.dsl.interpreter import DSLInterpreter
from imperiumengine.dsl.market_data import BinanceMarketDataProvider
from imperiumengine.dsl.parser import DSLParser
from imperiumengine.dsl.validators import StrategyValidator


def send_order_signal(order: dict) -> None:
    """
    Envia um sinal da ordem via HTTP.
    Substitua 'http://your-http-endpoint.com/signal' pelo endpoint desejado.
    """
    url = "https://webhook.site/096b9dca-8e4b-4145-88de-c42c9eeb0231"
    try:
        response = requests.post(url, json=order, timeout=5)
        response.raise_for_status()  # Levanta exceção para status HTTP 4xx/5xx
        print(f"Sinal enviado com sucesso: {order}")
    except Exception as e:
        print(f"Falha ao enviar sinal: {e}")


def load_strategy(file_path: str) -> list:
    """Carrega as instruções da estratégia a partir de um arquivo JSON."""
    with Path(file_path).open() as f:
        data = json.load(f)
    return data.get("instructions", [])


def main() -> None:
    logger = LogFactory.get_logger("Main")

    # Carrega a estratégia do arquivo JSON
    strategy_instructions = load_strategy("a.json")
    logger.info(f"Loaded {len(strategy_instructions)} instructions from file.")

    # Valida as instruções
    validator = StrategyValidator(strategy_instructions)
    valid, errors = validator.validate()
    if not valid:
        logger.error("Strategy Invalid! Errors found:")
        for err in errors:
            logger.error(err)
        return

    try:
        # Faz o parsing das instruções e monta a estrutura da estratégia
        root_instruction = DSLParser.parse(strategy_instructions)
    except Exception as e:
        logger.exception("Error parsing instructions: %s", e)
        return

    # Inicializa o provedor de dados do mercado (substitua as chaves pelas suas)
    market_data_provider = BinanceMarketDataProvider(
        api_key="YOUR_API_KEY", api_secret="YOUR_API_SECRET"
    )

    # Loop de monitoramento contínuo
    while True:
        try:
            # Cria uma nova instância do interpretador (ou reinicia o contexto, conforme sua necessidade)
            interpreter = DSLInterpreter(root_instruction, market_data_provider)

            # Carrega os dados de mercado (ajuste o símbolo, intervalo e limite conforme necessário)
            interpreter.load_market_data(
                symbol="DOGEUSDT", interval=Client.KLINE_INTERVAL_1MINUTE, limit=100
            )

            # Executa a estratégia definida
            interpreter.run()

            logger.info("Execution complete. Final state:")
            for key, value in interpreter.context.variables.items():
                logger.info(f"  {key}: {value}")

            # Se houver trades, envia um sinal para cada operação
            trades = interpreter.context.variables.get("trades", [])
            for trade in trades:
                # Exemplo de trade: {'action': 'buy', 'symbol': 'BTCUSDT', 'quantity': 1}
                send_order_signal(trade)

        except Exception as e:
            logger.exception("Error during strategy execution: %s", e)

        # Aguarda 60 segundos antes de buscar novos dados e reexecutar a estratégia
        time.sleep(60)


if __name__ == "__main__":
    main()
