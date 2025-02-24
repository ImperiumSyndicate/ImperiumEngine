import abc

from imperiumengine.config.logger import LogFactory

logger = LogFactory.get_logger("NewsCollectorBase")


class NewsCollectorBase(abc.ABC):
    """
    Template para módulos de coleta de notícias.
    """

    def __init__(self):
        self.data = {}

    @abc.abstractmethod
    def fetch_data(self):
        """
        Método abstrato para coletar dados de notícias.
        """
