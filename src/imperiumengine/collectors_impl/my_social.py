import random

from imperiumengine.collector.social_base import SocialCollectorBase
from imperiumengine.config.logger import LogFactory

logger = LogFactory.get_logger("MySocialCollector")


class MySocialCollector(SocialCollectorBase):
    def fetch_data(self):
        try:
            self.data["tweets"] = self._fetch_tweets()
            self.data["news_headlines"] = self._fetch_news_headlines()
            logger.info("Dados de social coletados: %s", self.data)
        except Exception as e:
            logger.error("Erro ao coletar dados de social: %s", e)

    def _fetch_tweets(self, num_tweets=70):
        base_tweets = [
            "Mercado em alta com oportunidades para investidores.",
            "A volatilidade do mercado exige cautela.",
            "Tendências positivas sinalizam um bom momento para compra.",
            "Alerta: riscos elevados no cenário atual.",
            "Movimentação intensa no mercado cripto.",
        ]
        return [random.choice(base_tweets) for _ in range(num_tweets)]

    def _fetch_news_headlines(self, num_headlines=70):
        base_headlines = [
            "Criptomoedas disparam após anúncio governamental.",
            "Investidores atentos à nova regulação do setor cripto.",
            "Mercado reage a mudanças nas políticas financeiras.",
            "Tendência de alta movimenta os preços das criptos.",
            "Alertas de volatilidade dominam o cenário financeiro.",
        ]
        return [random.choice(base_headlines) for _ in range(num_headlines)]
