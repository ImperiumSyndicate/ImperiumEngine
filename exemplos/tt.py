import time

from imperiumengine.analyzer import Analyzer
from imperiumengine.collectors_impl.my_news import MyNewsCollector
from imperiumengine.collectors_impl.my_onchain import MyOnchainCollector
from imperiumengine.collectors_impl.my_sentiment import MySentimentCollector
from imperiumengine.collectors_impl.my_social import MySocialCollector
from imperiumengine.collectors_impl.my_technical import MyTechnicalCollector
from imperiumengine.config.logger import LogFactory

logger = LogFactory.get_logger("ImperiumEngine")


def main():
    # Instancia os coletores concretos
    technical = MyTechnicalCollector()
    sentiment = MySentimentCollector()
    news = MyNewsCollector()
    onchain = MyOnchainCollector()
    social = MySocialCollector()

    # Realiza a coleta dos dados
    technical.fetch_data()
    sentiment.fetch_data()
    news.fetch_data()
    onchain.fetch_data()
    social.fetch_data()

    # Pequena pausa para garantir que os dados foram coletados (se necessário)
    time.sleep(1)

    # Injeta os coletores no analisador
    analyzer = Analyzer(technical, sentiment, news, onchain, social)
    final_score = analyzer.calculate_total_score()
    signal = analyzer.generate_signal()

    logger.info("Resultado Final: Score: %s | Sinal: %s", final_score, signal)


if __name__ == "__main__":
    main()
