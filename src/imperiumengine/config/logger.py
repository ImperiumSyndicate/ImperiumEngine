import logging


def setup_logger(name: str) -> logging.Logger:
    """
    Configura um logger com nível DEBUG e saída para o console.

    Parâmetros
    ----------
    name : str
        O nome do logger.

    Retorna
    -------
    logging.Logger
        Instância configurada de um logger.

    Exemplo
    --------
    >>> logger = setup_logger("meu_logger")
    >>> logger.info("Mensagem de informação")
    >>> logger.debug("Mensagem de depuração")
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # Formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)

    logger.addHandler(ch)
    return logger
