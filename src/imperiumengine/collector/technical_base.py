import abc

from imperiumengine.config.logger import LogFactory

logger = LogFactory.get_logger("TechnicalCollectorBase")


class TechnicalCollectorBase(abc.ABC):
    """
    Template para módulos de coleta de dados técnicos.
    """

    def __init__(self):
        self.data = {}

    @abc.abstractmethod
    def fetch_data(self):
        """
        Método abstrato para coletar dados técnicos.
        """
