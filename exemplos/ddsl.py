import json
from pathlib import Path

from binance.client import Client

from imperiumengine.config.logger import LogFactory
from imperiumengine.dsl.interpreter import DSLInterpreter
from imperiumengine.dsl.market_data import BinanceMarketDataProvider
from imperiumengine.dsl.parser import DSLParser
from imperiumengine.dsl.validators import StrategyValidator


def main() -> None:
    # Obtém o logger para o módulo "Main"
    logger = LogFactory.get_logger("Main")

    try:
        with Path("a.json").open() as f:
            data = json.load(f)
        instructions_list = data.get("instructions", [])
        logger.info(f"Loaded {len(instructions_list)} instructions from file.")
    except Exception as e:
        logger.exception("Error reading JSON file: %s", e)
        return

    validator = StrategyValidator(instructions_list)
    valid, errors = validator.validate()
    if valid:
        logger.info("Strategy Validated: Strategy is valid!")
    else:
        logger.error("Strategy Invalid! Errors found:")
        for err in errors:
            logger.error(err)
        return

    try:
        root_instruction = DSLParser.parse(instructions_list)
    except Exception as e:
        logger.exception("Error parsing instructions: %s", e)
        return

    market_data_provider = BinanceMarketDataProvider(api_key="", api_secret="")
    interpreter = DSLInterpreter(root_instruction, market_data_provider)

    try:
        interpreter.load_market_data(
            symbol="BTCUSDT", interval=Client.KLINE_INTERVAL_1HOUR, limit=100
        )
    except Exception as e:
        logger.exception("Aborting: Unable to load market data: %s", e)
        return

    try:
        interpreter.run()
    except Exception as e:
        logger.exception("Strategy execution failed: %s", e)
        return

    logger.info("Execution complete. Final state:")
    for key, value in interpreter.context.variables.items():
        logger.info(f"  {key}: {value}")


if __name__ == "__main__":
    main()
