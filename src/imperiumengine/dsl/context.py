from typing import Any


class Context:
    """
    Contexto de execução que armazena variáveis.

    Esta classe fornece um contêiner simples para armazenar e gerenciar variáveis durante a execução
    de uma aplicação ou de uma DSL. O contexto utiliza um dicionário para manter o estado e permite
    atualizações dinâmicas dos dados através do método `update`.

    Attributes
    ----------
    variables : dict[str, Any]
        Dicionário que armazena as variáveis do contexto.

    Methods
    -------
    update(data: dict[str, Any]) -> None
        Atualiza o dicionário de variáveis com os valores fornecidos em `data`.

    Examples
    --------
    >>> ctx = Context()
    >>> ctx.variables
    {}
    >>> ctx.update({"a": 1, "b": 2})
    >>> ctx.variables
    {'a': 1, 'b': 2}
    """

    def __init__(self) -> None:
        """
        Inicializa uma nova instância de Context com um dicionário vazio de variáveis.
        """
        self.variables: dict[str, Any] = {}

    def update(self, data: dict[str, Any]) -> None:
        """
        Atualiza o contexto com os dados fornecidos.

        Este método recebe um dicionário e atualiza o dicionário interno `variables` com os
        pares chave-valor presentes em `data`. Se uma chave já existir, seu valor será atualizado;
        caso contrário, a chave será adicionada.

        Parameters
        ----------
        data : dict[str, Any]
            Dicionário contendo os dados a serem atualizados no contexto.

        Examples
        --------
        >>> ctx = Context()
        >>> ctx.update({"x": 10})
        >>> ctx.variables
        {'x': 10}
        >>> ctx.update({"y": 20})
        >>> ctx.variables
        {'x': 10, 'y': 20}
        """
        self.variables.update(data)
