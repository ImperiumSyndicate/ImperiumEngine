class DSLError(Exception):
    """
    Erro relacionado à DSL (Domain Specific Language).

    Esta exceção é lançada sempre que ocorre um problema durante a avaliação ou execução de
    expressões e instruções definidas na DSL. Ela pode ser utilizada para sinalizar erros de
    sintaxe, semântica ou de segurança, garantindo que apenas operações permitidas sejam realizadas.

    Parameters
    ----------
    message : str
        Explicação detalhada do erro ocorrido.


    Traceback (most recent call last):
      ...
    DSLError: Operação inválida na DSL.
    """
