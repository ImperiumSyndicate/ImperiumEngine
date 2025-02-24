import random

from imperiumengine.collector.onchain_base import OnchainCollectorBase
from imperiumengine.config.logger import LogFactory

logger = LogFactory.get_logger("MyOnchainCollector")


class MyOnchainCollector(OnchainCollectorBase):
    def fetch_data(self):
        try:
            self.data = {
                "whale_movements": random.randint(0, 10),
                "addresses_active": random.randint(1000, 5000),
                "new_wallets": random.randint(10, 100),
                "active_addresses_1btc": random.randint(100, 500),
                "gas_fees": random.uniform(20, 100),
            }
            logger.info("Dados onchain coletados: %s", self.data)
        except Exception as e:
            logger.error("Erro ao coletar dados onchain: %s", e)
