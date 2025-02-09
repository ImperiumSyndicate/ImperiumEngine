from pathlib import Path

import toml

DEFAULT_CONFIG_PATHS = ["./config.toml", "~/.config/myapp/config.toml", "/etc/myapp/config.toml"]


class ImperiumengineConfig:
    _instance = None

    def __new__(cls, config_file: str = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(config_file)  # noqa: SLF001
        return cls._instance

    def _initialize(self, config_file: str = None):
        """
        Inicializa a instância carregando o arquivo de configuração.

        Se `config_file` for fornecido, converte-o para um objeto `Path` e expande
        o usuário. Caso contrário, procura um arquivo de configuração nos caminhos
        padrão definidos em DEFAULT_CONFIG_PATHS.
        """
        if config_file:
            self.config_file = Path(config_file).expanduser()
        else:
            self.config_file = self._find_default_config()
        self.config_data = self._load_config()

    def _find_default_config(self) -> Path:
        """
        Procura um arquivo de configuração nos caminhos padrão.

        Returns
        -------
        Path
            O caminho para o primeiro arquivo encontrado.

        Raises
        ------
        FileNotFoundError
            Se nenhum arquivo for encontrado nos diretórios padrão.
        """
        for path in DEFAULT_CONFIG_PATHS:
            full_path = Path(path).expanduser()
            if full_path.exists():
                return full_path
        raise FileNotFoundError("Nenhum arquivo de configuração encontrado nos diretórios padrões.")

    def _load_config(self):
        """
        Carrega as configurações do arquivo TOML.

        Returns
        -------
        dict
            Dicionário com as configurações carregadas.

        Raises
        ------
        FileNotFoundError
            Se o arquivo de configuração não for encontrado.
        ValueError
            Se ocorrer um erro ao decodificar o arquivo TOML.
        """
        try:
            with self.config_file.open(encoding="utf-8") as file:
                return toml.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo de configuração '{self.config_file}' não encontrado.")
        except toml.TomlDecodeError:
            raise ValueError(f"Erro ao decodificar o arquivo TOML: '{self.config_file}'.")

    def get(self, key: str, default=None):
        """
        Obtém um valor da configuração com base na chave fornecida.

        A chave pode estar aninhada, sendo separada por pontos.

        Parameters
        ----------
        key : str
            A chave da configuração (por exemplo, "sentry.dsn").
        default
            Valor padrão a ser retornado caso a chave não seja encontrada.

        Returns
        -------
        O valor associado à chave ou o valor padrão se não encontrado.
        """
        keys = key.split(".")
        value = self.config_data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def reload(self):
        """
        Recarrega as configurações do arquivo TOML.
        """
        self.config_data = self._load_config()

    @classmethod
    def set_config_file(cls, file_path: str):
        """
        Define um novo arquivo de configuração e recarrega os dados.

        Parameters
        ----------
        file_path : str
            O caminho para o novo arquivo de configuração.

        Returns
        -------
        ImperiumengineConfig
            A instância atualizada da configuração.

        Raises
        ------
        FileNotFoundError
            Se o arquivo de configuração não for encontrado.
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"Arquivo de configuração '{file_path}' não encontrado.")
        cls._instance = None  # Reseta a instância
        return cls(file_path)
