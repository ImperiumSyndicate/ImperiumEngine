import random

from imperiumengine.collector.news_base import NewsCollectorBase
from imperiumengine.config.logger import LogFactory

logger = LogFactory.get_logger("MyNewsCollector")


class MyNewsCollector(NewsCollectorBase):
    def fetch_data(self):
        try:
            self.data = {
                "latest_headline": "O governo dos EUA anunciou novas políticas de regulação para criptomoedas.",
                "source": random.choice(["CoinDesk", "CoinTelegraph", "Reuters", "Bloomberg"]),
                "impact": random.randint(1, 100),
            }
            logger.info("Dados de notícias coletados: %s", self.data)
        except Exception as e:
            logger.error("Erro ao coletar dados de notícias: %s", e)
