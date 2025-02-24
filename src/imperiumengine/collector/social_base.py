import abc

from imperiumengine.config.logger import LogFactory

logger = LogFactory.get_logger("SocialCollectorBase")


class SocialCollectorBase(abc.ABC):
    """
    Template para módulos de coleta de dados de redes sociais.
    """

    def __init__(self):
        self.data = {"tweets": [], "news_headlines": []}

    @abc.abstractmethod
    def fetch_data(self):
        """
        Método abstrato para coletar dados de redes sociais.
        """
