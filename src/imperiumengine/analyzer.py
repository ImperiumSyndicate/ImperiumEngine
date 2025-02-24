from imperiumengine.config.logger import LogFactory

logger = LogFactory.get_logger("Analyzer")


class Analyzer:
    """
    Analisa os dados coletados para gerar um score e sinal de negociação.
    As dependências (coletores) são injetadas via construtor.
    """

    def __init__(self, technical, sentiment, news, onchain, social, weights=None):
        self.technical = technical
        self.sentiment = sentiment
        self.news = news
        self.onchain = onchain
        self.social = social
        self.weights = weights or {
            "technical": 35,
            "sentiment": 25,
            "news": 22.5,
            "onchain": 17.5,
        }

    def calculate_technical_score(self):
        try:
            data = self.technical.data
            score = data.get("market_value", 35000) / 1000  # exemplo de cálculo
            logger.info("Score Técnico calculado: %s", score)
            return score
        except Exception as e:
            logger.error("Erro no cálculo do score técnico: %s", e)
            return 70

    def calculate_sentiment_score_numeric(self):
        try:
            data = self.sentiment.data
            sentiment_text = data.get("social_text", "NEUTRO")
            mapping = {"NEGATIVO": 40, "NEUTRO": 70, "POSITIVO": 90}
            numeric_value = mapping.get(sentiment_text, 70)
            logger.info("Score de Sentimento numérico: %s", numeric_value)
            return numeric_value
        except Exception as e:
            logger.error("Erro no cálculo do score de sentimento: %s", e)
            return 70

    def calculate_news_score(self):
        try:
            data = self.news.data
            score = data.get("impact", 50)
            logger.info("Score de Notícias calculado: %s", score)
            return score
        except Exception as e:
            logger.error("Erro no cálculo do score de notícias: %s", e)
            return 50

    def calculate_onchain_score(self):
        try:
            data = self.onchain.data
            score = data.get("gas_fees", 50)
            logger.info("Score Onchain calculado: %s", score)
            return score
        except Exception as e:
            logger.error("Erro no cálculo do score onchain: %s", e)
            return 70

    def calculate_total_score(self):
        try:
            t = self.calculate_technical_score()
            s = self.calculate_sentiment_score_numeric()
            n = self.calculate_news_score()
            o = self.calculate_onchain_score()
            total_weight = sum(self.weights.values())
            weighted_sum = (
                t * self.weights["technical"]
                + s * self.weights["sentiment"]
                + n * self.weights["news"]
                + o * self.weights["onchain"]
            )
            total_score = weighted_sum / total_weight
            logger.info("Score Total calculado: %s", total_score)
            return total_score
        except Exception as e:
            logger.error("Erro no cálculo do score total: %s", e)
            return 70

    def generate_signal(self, threshold=75):
        try:
            score = self.calculate_total_score()
            signal = "BUY" if score >= threshold else "SELL"
            logger.info("Sinal Gerado: %s", signal)
            return signal
        except Exception as e:
            logger.error("Erro na geração do sinal: %s", e)
            return "HOLD"
