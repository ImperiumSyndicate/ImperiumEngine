from pathlib import Path
from typing import Any, Optional

import toml

DEFAULT_CONFIG_PATHS = ["./config.toml", "~/.config/myapp/config.toml", "/etc/myapp/config.toml"]


class ImperiumengineConfig:
    """
    Gerencia o carregamento e acesso às configurações de uma aplicação a partir de um arquivo TOML.

    Esta classe implementa o padrão singleton para que apenas uma instância com as configurações
    seja utilizada durante a execução da aplicação. Ela permite a busca por arquivos de configuração
    em caminhos padrão e oferece métodos para carregar, recarregar e acessar as configurações de forma
    estruturada.

    Atributos
    ---------
    _instance : Optional[ImperiumengineConfig]
        Instância única da classe. Utilizada para implementar o padrão singleton.
    config_file : Optional[Path]
        Caminho do arquivo de configuração atualmente utilizado.
    config_data : dict[str, Any]
        Dicionário contendo as configurações carregadas do arquivo TOML.

    Exemplos
    --------
    >>> config = ImperiumengineConfig()
    >>> valor = config.get("sentry.dsn", default="valor_default")
    >>> print(valor)
    valor_default
    """

    _instance: Optional["ImperiumengineConfig"] = None

    def __new__(cls, config_file: str | None = None) -> "ImperiumengineConfig":
        """
        Cria ou retorna a instância única da classe.

        Se uma instância ainda não existir, a mesma é criada e o arquivo de configuração
        é carregado utilizando `initialize_config`.

        Parameters
        ----------
        config_file : str or None, optional
            Caminho para o arquivo de configuração. Se None, a busca é realizada
            pelos caminhos padrão definidos em DEFAULT_CONFIG_PATHS.

        Returns
        -------
        ImperiumengineConfig
            A instância única com as configurações carregadas.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialize_config(config_file)
        return cls._instance

    def initialize_config(self, config_file: str | None = None) -> None:
        """
        Inicializa a instância carregando o arquivo de configuração.

        Se `config_file` for fornecido, converte-o para um objeto `Path` e expande o usuário.
        Caso contrário, procura um arquivo de configuração nos caminhos padrão definidos em
        DEFAULT_CONFIG_PATHS. Se nenhum arquivo for encontrado, a configuração é definida como
        um dicionário vazio.

        Parameters
        ----------
        config_file : str or None, optional
            Caminho para o arquivo de configuração. O padrão é None.

        Returns
        -------
        None

        Exemplos
        --------
        >>> config = ImperiumengineConfig("config.toml")
        """
        if config_file:
            self.config_file = Path(config_file).expanduser()
        else:
            try:
                self.config_file = self._find_default_config()
            except FileNotFoundError:
                self.config_file = None

        # Tenta carregar o arquivo se houver; caso contrário, define config_data como {}
        if self.config_file is not None:
            try:
                self.config_data = self._load_config()
            except (FileNotFoundError, ValueError):
                self.config_data = {}
        else:
            self.config_data = {}

    def _find_default_config(self) -> Path:
        """
        Procura um arquivo de configuração nos caminhos padrão.

        Percorre os caminhos listados em DEFAULT_CONFIG_PATHS e retorna o primeiro arquivo
        que for encontrado.

        Returns
        -------
        Path
            Caminho para o primeiro arquivo de configuração encontrado.

        Raises
        ------
        FileNotFoundError
            Se nenhum arquivo de configuração for encontrado nos caminhos padrão.


        """
        for path in DEFAULT_CONFIG_PATHS:
            full_path = Path(path).expanduser()
            if full_path.exists():
                return full_path
        raise FileNotFoundError("Nenhum arquivo de configuração encontrado nos diretórios padrões.")

    def _load_config(self) -> dict[str, Any]:
        """
        Carrega as configurações do arquivo TOML.

        Abre o arquivo de configuração e utiliza a biblioteca `toml` para decodificar
        seu conteúdo em um dicionário.

        Returns
        -------
        dict[str, Any]
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

    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtém um valor da configuração com base na chave fornecida.

        A chave pode ser composta e aninhada, utilizando o ponto como separador.
        O método percorre o dicionário de configuração e retorna o valor associado ou
        o valor padrão se a chave não for encontrada.

        Parameters
        ----------
        key : str
            Chave da configuração (por exemplo, "sentry.dsn").
        default : Any, optional
            Valor a ser retornado se a chave não for encontrada. O padrão é None.

        Returns
        -------
        Any
            Valor associado à chave ou o valor padrão.


        """
        keys = key.split(".")
        value = self.config_data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def reload(self) -> None:
        """
        Recarrega as configurações a partir do arquivo TOML.

        Se um arquivo de configuração estiver definido, tenta recarregá-lo e atualizar
        o dicionário de configurações. Caso contrário, define as configurações como um dicionário vazio.

        Returns
        -------
        None

        Exemplos
        --------
        >>> config = ImperiumengineConfig("config.toml")
        >>> config.reload()
        """
        if self.config_file is not None:
            try:
                self.config_data = self._load_config()
            except (FileNotFoundError, ValueError):
                self.config_data = {}
        else:
            self.config_data = {}

    @classmethod
    def set_config_file(cls, file_path: str) -> "ImperiumengineConfig":
        """
        Define um novo arquivo de configuração e recarrega os dados.

        Este método permite alterar o arquivo de configuração em tempo de execução.
        Ele valida a existência do arquivo, reseta a instância singleton e cria
        uma nova instância com o arquivo especificado.

        Parameters
        ----------
        file_path : str
            Caminho para o novo arquivo de configuração.

        Returns
        -------
        ImperiumengineConfig
            Nova instância com as configurações carregadas a partir do arquivo especificado.

        Raises
        ------
        FileNotFoundError
            Se o arquivo de configuração fornecido não for encontrado.


        """
        new_path = Path(file_path).expanduser()
        if not new_path.exists():
            raise FileNotFoundError(f"Arquivo de configuração '{new_path}' não encontrado.")
        cls._instance = None  # Reseta a instância para carregar nova configuração
        return cls(file_path)
