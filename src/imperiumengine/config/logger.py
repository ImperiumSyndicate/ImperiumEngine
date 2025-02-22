import logging
import tempfile
from pathlib import Path

from colorama import Fore, Style, init

# Inicializa o Colorama para habilitar as cores no terminal
init(autoreset=True)

# Tenta importar o handler para Graylog (pygelf)
try:
    from pygelf import GelfUdpHandler

    HAS_PYGELF = True
except ImportError:
    HAS_PYGELF = False

# Tenta importar o SDK do Sentry
try:
    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration

    HAS_SENTRY = True
except ImportError:
    HAS_SENTRY = False


class ColoredFormatter(logging.Formatter):
    """
    Formatter que adiciona cores às mensagens de log de acordo com o nível.

    Essa classe estende `logging.Formatter` e aplica códigos de cor ANSI às mensagens
    de log com base no nível de severidade (DEBUG, INFO, WARNING, ERROR, CRITICAL).

    Attributes
    ----------
    LEVEL_COLOR : dict[int, str]
        Dicionário que mapeia níveis de log (como `logging.DEBUG`) para seus respectivos
        códigos de cor ANSI do Colorama.

    Methods
    -------
    format(record: logging.LogRecord) -> str
        Formata o registro de log, aplicando a cor definida para o nível do registro.

    Examples
    --------
    >>> import logging
    >>> from colorama import init, Fore, Style
    >>> init(autoreset=True)
    >>> formatter = ColoredFormatter("%(levelname)s: %(message)s")
    >>> record = logging.LogRecord("test", logging.INFO, "", 0, "Teste de log", None, None)
    >>> formatted = formatter.format(record)
    >>> # Verifica se a string contém o código de cor associado ao INFO
    >>> Fore.GREEN in formatted or Style.RESET_ALL in formatted
    True
    """

    LEVEL_COLOR: dict[int, str] = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT,
    }

    def format(self, record: logging.LogRecord) -> str:
        """
        Formata o registro de log aplicando a cor correspondente ao seu nível.

        Parameters
        ----------
        record : logging.LogRecord
            Registro de log que contém os dados da mensagem e seu nível de severidade.

        Returns
        -------
        str
            A mensagem formatada com os códigos de cor ANSI aplicados.
        """
        color: str = self.LEVEL_COLOR.get(record.levelno, "")
        # Aplica a cor ao texto da mensagem
        record.msg = f"{color}{record.msg}{Style.RESET_ALL}"
        return super().format(record)


class LogFactory:
    """
    Fábrica centralizada para criação e configuração dos loggers.

    Essa classe gerencia a configuração global dos logs utilizando as seguintes integrações:
      - **Sentry:** Para monitoramento de erros e performance.
      - **Graylog:** Para centralização de logs via UDP.
      - **Fallback Local:** Caso nenhuma das integrações esteja configurada, os logs são
        gravados em arquivos locais em diretórios temporários.

    A configuração é obtida a partir de uma instância externa da classe
    `ImperiumengineConfig` (gerenciada via TOML). Se a instância não estiver disponível,
    é utilizado um fallback para gravação local.

    Attributes
    ----------
    _loggers : dict[str, logging.Logger]
        Dicionário que armazena os loggers criados, mapeando o nome para a instância do logger.
    _configured : bool
        Flag que indica se o logger raiz já foi configurado.

    Methods
    -------
    configure() -> None
        Configura o logger raiz com os handlers e integrações apropriadas.
    get_logger(name: str) -> logging.Logger
        Retorna uma instância de logger com o nome especificado.

    Examples
    --------
    >>> # Exemplo de obtenção e uso de um logger (exemplo ignorado no doctest)
    >>> logger = LogFactory.get_logger("MeuLogger")  # doctest: +SKIP
    >>> logger.info("Log de informação")  # doctest: +SKIP
    """

    _loggers: dict[str, logging.Logger] = {}
    _configured: bool = False

    @classmethod
    def configure(cls) -> None:
        """
        Configura o logger raiz com handlers e integrações (Sentry, Graylog ou fallback local).

        Este método tenta obter uma instância da configuração via `ImperiumengineConfig`. Se essa
        instância estiver disponível, utiliza as configurações definidas para Sentry e Graylog.
        Caso contrário, é utilizado um fallback que grava logs e tracking em arquivos locais
        dentro de um diretório temporário.

        Adicionalmente, é sempre adicionado um `StreamHandler` para exibir os logs no terminal
        com formatação colorida.

        Returns
        -------
        None

        Examples
        --------
        >>> # Reset para garantir que a configuração seja aplicada
        >>> LogFactory._configured = False
        >>> LogFactory.configure()
        """
        if cls._configured:
            return

        root_logger: logging.Logger = logging.getLogger()
        use_sentry: bool = False
        use_graylog: bool = False

        # Tenta obter a instância da classe Config (que utiliza TOML)
        try:
            from imperiumengine.config.imperiumengine_settings import ImperiumengineConfig

            config_instance = ImperiumengineConfig()
        except Exception as e:
            config_instance = None
            root_logger.warning("Não foi possível obter a instância de Config: %s", e)

        if config_instance is not None:
            # --- Integração com Sentry ---
            dsn: str = config_instance.get("sentry.dsn", "").strip()
            if dsn:
                use_sentry = True
                environment: str = config_instance.get("sentry.environment", "production")
                if HAS_SENTRY:
                    sentry_logging = LoggingIntegration(
                        level=logging.INFO,  # Captura breadcrumbs a partir do INFO
                        event_level=logging.ERROR,  # Erros são enviados como eventos para o Sentry
                    )
                    sentry_sdk.init(
                        dsn=dsn,
                        integrations=[sentry_logging],
                        environment=environment,
                        traces_sample_rate=1.0,  # Habilita o tracing (monitoramento de performance)
                    )
                    root_logger.info("Sentry configurado com sucesso (via TOML).")
                else:
                    root_logger.warning(
                        "Configuração para Sentry encontrada, mas o pacote sentry-sdk não está instalado."
                    )
            else:
                root_logger.info("Sentry não configurado (via TOML).")

            # --- Integração com Graylog ---
            host: str = config_instance.get("graylog.host", "").strip()
            if host:
                use_graylog = True
                port: int = config_instance.get("graylog.port", 12201)
                if HAS_PYGELF:
                    graylog_handler = GelfUdpHandler(host=host, port=int(port))
                    graylog_handler.setLevel(logging.DEBUG)
                    root_logger.addHandler(graylog_handler)
                    root_logger.info("Graylog configurado com sucesso (via TOML).")
                else:
                    root_logger.warning(
                        "Configuração para Graylog encontrada, mas o pacote pygelf não está instalado."
                    )
            else:
                root_logger.info("Graylog não configurado (via TOML).")
        else:
            root_logger.info("Instância de Config não disponível. Utilizando fallback local.")

        # --- Fallback Local: grava logs e tracking em arquivos ---
        if not use_sentry and not use_graylog:
            project_name: str = "ImperiumEngine"
            tmp_dir: Path = Path(tempfile.gettempdir()) / project_name
            log_dir: Path = tmp_dir / "log"
            tracking_dir: Path = tmp_dir / "tracking"
            log_dir.mkdir(parents=True, exist_ok=True)
            tracking_dir.mkdir(parents=True, exist_ok=True)
            log_file: Path = log_dir / "app.log"
            tracking_file: Path = tracking_dir / "tracking.log"

            # Handler para logs gerais com formatação colorida
            file_handler = logging.FileHandler(str(log_file))
            file_formatter = ColoredFormatter(
                "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
            )
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)

            # Handler para tracking com formatação JSON-like
            tracking_handler = logging.FileHandler(str(tracking_file))
            tracking_formatter = logging.Formatter(
                '{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            tracking_handler.setFormatter(tracking_formatter)
            root_logger.addHandler(tracking_handler)

            root_logger.info(
                "Fallback local: logs serão gravados em '%s' e tracking em '%s'",
                log_dir,
                tracking_dir,
            )

        # --- Adiciona um StreamHandler para exibir os logs no terminal ---
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(
            ColoredFormatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        )
        root_logger.addHandler(stream_handler)
        root_logger.setLevel(logging.DEBUG)
        cls._configured = True

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Retorna um logger com o nome especificado, garantindo que a configuração global seja aplicada.

        Se o logger com o nome fornecido ainda não foi criado, este método o cria, armazena na
        fábrica e retorna a instância correspondente.

        Parameters
        ----------
        name : str
            Nome do logger a ser obtido.

        Returns
        -------
        logging.Logger
            Instância do logger associada ao nome informado.

        Examples
        --------
        >>> logger = LogFactory.get_logger("ExampleLogger")
        >>> isinstance(logger, logging.Logger)
        True
        """
        if not cls._configured:
            cls.configure()
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            cls._loggers[name] = logger
        return cls._loggers[name]
