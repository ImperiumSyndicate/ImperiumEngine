import json
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
    Substitua 'https://webhook.site/f242460a-8a0a-458b-9d33-c1c5471281a6' pelo endpoint desejado.
    """
    url = "https://webhook.site/f242460a-8a0a-458b-9d33-c1c5471281a6"
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


def execute_strategy_iteration(root_instruction, market_data_provider, logger) -> None:
    """
    Executa uma iteração da estratégia.
    """
    interpreter = DSLInterpreter(root_instruction, market_data_provider)
    interpreter.load_market_data(
        symbol="DOGEUSDT", interval=Client.KLINE_INTERVAL_1MINUTE, limit=100
    )
    interpreter.run()

    logger.info("Execution complete. Final state:")
    for key, value in interpreter.context.variables.items():
        logger.info(f"  {key}: {value}")

    trades = interpreter.context.variables.get("trades", [])
    for trade in trades:
        send_order_signal(trade)


def safe_execute_strategy(root_instruction, market_data_provider, logger) -> None:
    """
    Envolve a execução de uma iteração da estratégia em um bloco try-except.
    Essa função isola o try-except, evitando seu uso direto no loop.
    """
    try:
        execute_strategy_iteration(root_instruction, market_data_provider, logger)
    except Exception as e:
        logger.exception("Error during strategy execution: %s", e)


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
        safe_execute_strategy(root_instruction, market_data_provider, logger)


if __name__ == "__main__":
    main()
