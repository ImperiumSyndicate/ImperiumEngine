import abc

from imperiumengine.config.logger import LogFactory

logger = LogFactory.get_logger("OnchainCollectorBase")


class OnchainCollectorBase(abc.ABC):
    """
    Template para módulos de coleta de dados onchain.
    """

    def __init__(self):
        self.data = {}

    @abc.abstractmethod
    def fetch_data(self):
        """
        Método abstrato para coletar dados onchain.
        """
