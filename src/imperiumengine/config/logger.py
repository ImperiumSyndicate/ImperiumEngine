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
    Formatter que adiciona cores às mensagens de log de acordo com o nível,
    se a opção `use_color` estiver ativada.

    Attributes
    ----------
    LEVEL_COLOR : dict[int, str]
        Dicionário que mapeia níveis de log para os códigos de cor ANSI do Colorama.
    use_color : bool
        Indica se a formatação com cores deve ser aplicada.

    Methods
    -------
    format(record: logging.LogRecord) -> str
        Formata o registro de log aplicando a cor definida para o nível do registro
        se `use_color` for True.
    """

    LEVEL_COLOR: dict[int, str] = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT,
    }

    def __init__(self, fmt: str = None, datefmt: str = None, use_color: bool = True):
        """
        Inicializa o formatter.

        Parameters
        ----------
        fmt : str, optional
            Formato da mensagem de log.
        datefmt : str, optional
            Formato da data/hora.
        use_color : bool, optional
            Indica se o formatter deve aplicar cores à mensagem. O padrão é True.
        """
        super().__init__(fmt, datefmt)
        self.use_color = use_color

    def format(self, record: logging.LogRecord) -> str:
        """
        Formata o registro de log aplicando a cor correspondente, caso `use_color` seja True.

        Parameters
        ----------
        record : logging.LogRecord
            Registro de log contendo as informações da mensagem e seu nível.

        Returns
        -------
        str
            Mensagem formatada (colorida se `use_color` for True, ou bruta caso contrário).
        """
        if self.use_color:
            color: str = self.LEVEL_COLOR.get(record.levelno, "")
            # Aplica a cor à mensagem e reseta o estilo ao final
            record.msg = f"{color}{record.msg}{Style.RESET_ALL}"
        return super().format(record)


class LogFactory:
    """
    Fábrica centralizada para criação e configuração dos loggers.

    Esta classe gerencia a configuração global dos logs, integrando:
      - **Sentry:** Monitoramento de erros e performance.
      - **Graylog:** Centralização de logs via UDP.
      - **Fallback Local:** Gravação de logs em arquivos locais (em diretórios temporários)
        caso as integrações acima não estejam configuradas.

    A configuração é, preferencialmente, obtida a partir de uma instância externa da classe
    `ImperiumengineConfig`. Se esta não estiver disponível, utiliza-se o fallback local.

    Attributes
    ----------
    _loggers : dict[str, logging.Logger]
        Dicionário que mapeia nomes de loggers para suas respectivas instâncias.
    _configured : bool
        Flag que indica se o logger raiz já foi configurado.

    Methods
    -------
    configure() -> None
        Configura o logger raiz com os handlers e integrações apropriadas.
    get_logger(name: str) -> logging.Logger
        Retorna uma instância de logger com o nome especificado.
    """

    _loggers: dict[str, logging.Logger] = {}
    _configured: bool = False

    @classmethod
    def configure(cls) -> None:
        """
        Configura o logger raiz com handlers e integrações (Sentry, Graylog ou fallback local).

        O método tenta obter uma instância de configuração via `ImperiumengineConfig`.
        Se disponível, utiliza as configurações definidas para Sentry e Graylog. Caso contrário,
        aplica um fallback que grava os logs em arquivos locais (em diretórios temporários).

        Adicionalmente, um `StreamHandler` é sempre adicionado para exibir os logs no terminal
        com formatação colorida.

        Returns
        -------
        None
        """
        if cls._configured:
            return

        root_logger: logging.Logger = logging.getLogger()
        use_sentry: bool = False
        use_graylog: bool = False

        # Tenta obter a instância de configuração via ImperiumengineConfig
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
                        level=logging.INFO,  # Captura breadcrumbs a partir do nível INFO
                        event_level=logging.ERROR,  # Erros são enviados como eventos para o Sentry
                    )
                    sentry_sdk.init(
                        dsn=dsn,
                        integrations=[sentry_logging],
                        environment=environment,
                        traces_sample_rate=1.0,  # Habilita o tracing para monitoramento de performance
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
                    # Utiliza um formatter sem cores para Graylog (formatação bruta)
                    plain_formatter = logging.Formatter(
                        "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
                    )
                    graylog_handler.setFormatter(plain_formatter)
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

            # Handler para logs gerais com formatação colorida (exibe no terminal ou arquivo)
            file_handler = logging.FileHandler(str(log_file))
            file_formatter = ColoredFormatter(
                "%(asctime)s [%(levelname)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                use_color=False,  # Fallback: logs enviados para arquivo sem cores
            )
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)

            # Handler para tracking com formatação em estilo JSON-like (sem cores)
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

        # --- Adiciona um StreamHandler para exibir os logs no terminal com cores ---
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(
            ColoredFormatter(
                "%(asctime)s [%(levelname)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                use_color=True,
            )
        )
        root_logger.addHandler(stream_handler)
        root_logger.setLevel(logging.DEBUG)
        cls._configured = True

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Retorna um logger com o nome especificado, garantindo que a configuração global seja aplicada.

        Se o logger com o nome fornecido ainda não foi criado, este método o cria,
        armazena na fábrica e retorna a instância correspondente.

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
