import random

from imperiumengine.collector.sentiment_base import SentimentCollectorBase
from imperiumengine.config.logger import LogFactory

logger = LogFactory.get_logger("MySentimentCollector")


class MySentimentCollector(SentimentCollectorBase):
    def fetch_data(self):
        try:
            self.data = {
                "twitter_mentions": random.randint(100, 1000),
                "reddit_mentions": random.randint(50, 500),
                "fear_and_greed": random.choice(["Medo Extremo", "Medo", "Neutral", "Ganância"]),
                "google_trends": random.randint(1, 100),
                "social_text": "NEUTRO",
            }
            logger.info("Dados de sentimento coletados: %s", self.data)
        except Exception as e:
            logger.error("Erro ao coletar dados de sentimento: %s", e)
