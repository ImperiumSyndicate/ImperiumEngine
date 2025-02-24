import random

from imperiumengine.collector.technical_base import TechnicalCollectorBase
from imperiumengine.config.logger import LogFactory

logger = LogFactory.get_logger("MyTechnicalCollector_nome_modulo")


class MyTechnicalCollector(TechnicalCollectorBase):
    def fetch_data(self):
        try:
            self.data = {
                "market_value": random.uniform(30000, 40000),
                "min_day": random.uniform(28000, 30000),
                "volume": random.uniform(1000, 5000),
                "dominance": random.uniform(40, 60),
                "RSI": random.uniform(30, 70),
                "ATR": random.uniform(100, 300),
                "EMA": random.uniform(30000, 40000),
                "Bollinger": (random.uniform(29000, 31000), random.uniform(39000, 41000)),
                "MACD": random.uniform(-50, 50),
                "VWAP": random.uniform(30000, 40000),
            }
            logger.info("Dados técnicos coletados: %s", self.data)
        except Exception as e:
            logger.error("Erro ao coletar dados técnicos: %s", e)
