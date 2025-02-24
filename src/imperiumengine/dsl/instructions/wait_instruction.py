import time

from imperiumengine.config.logger import LogFactory
from imperiumengine.dsl.context import Context
from imperiumengine.dsl.exceptions import DSLError
from imperiumengine.dsl.instructions.instruction import Instruction

MIN_WAIT_LENGTH = 2  # Tempo mínimo de espera para evitar valores muito baixos


class WaitInstruction(Instruction):
    """
    Instrução de espera que pausa a execução por um determinado período.

    Esta instrução realiza uma pausa na execução utilizando a função `time.sleep`.
    O tempo de espera pode ser especificado como um valor numérico (int ou float) ou como uma
    string que contenha um valor numérico seguido de uma unidade de tempo. As unidades suportadas
    são:
      - 's' para segundos;
      - 'm' para minutos;
      - 'h' para horas.

    Se o valor de espera informado for inferior a {MIN_WAIT_LENGTH} segundos, o tempo de espera
    será ajustado para {MIN_WAIT_LENGTH} segundos, garantindo uma pausa mínima.

    Parameters
    ----------
    duration : int, float ou str
        Valor que representa o tempo de espera. Se for numérico, é interpretado em segundos.
        Se for uma string, deve ser um número seguido de uma unidade ('s', 'm' ou 'h').
        Exemplos:
          - 5 ou 5.0: 5 segundos;
          - '3s': 3 segundos;
          - '1.5m': 90 segundos;
          - '0.5h': 1800 segundos.

    Attributes
    ----------
    duration : float
        Duração da espera em segundos, após a conversão e validação.
    logger : logging.Logger
        Logger utilizado para registrar mensagens, avisos e erros durante a execução.

    Raises
    ------
    DSLError
        Se a unidade de tempo na string for inválida (diferente de 's', 'm' ou 'h') ou se o
        formato for incorreto.
    TypeError
        Se o valor informado não for numérico nem uma string com unidade.

    Examples
    --------
    >>> import time
    >>> from imperiumengine.dsl.context import Context
    >>> context = Context()
    >>> # Exemplo com valor numérico inferior ao mínimo (1 segundo é ajustado para 2 segundos)
    >>> w = WaitInstruction(1)
    >>> inicio = time.time()
    >>> w.execute(context)
    >>> elapsed = time.time() - inicio
    >>> elapsed >= 2
    True
    >>> # Exemplo com string e unidade: '3s' para 3 segundos
    >>> w2 = WaitInstruction("3s")
    >>> inicio = time.time()
    >>> w2.execute(context)
    >>> elapsed = time.time() - inicio
    >>> elapsed >= 3
    True
    """

    def __init__(self, duration: any) -> None:
        """
        Inicializa a instrução de espera com a duração especificada.

        Converte o valor informado para segundos, de acordo com o tipo e a unidade especificada.
        Caso o valor seja numérico, ele é interpretado diretamente como segundos. Se for uma string,
        o último caractere é considerado a unidade de tempo e o restante é convertido para float.

        Parameters
        ----------
        duration : int, float ou str
            Valor que representa o tempo de espera. Exemplos:
              - 5 ou 5.0: 5 segundos;
              - '3s': 3 segundos;
              - '1.5m': 90 segundos;
              - '0.5h': 1800 segundos.

        Raises
        ------
        DSLError
            Se a unidade de tempo na string for inválida (diferente de 's', 'm' ou 'h') ou se o
            formato for incorreto.
        TypeError
            Se o valor informado não for numérico nem uma string com unidade.
        """
        self.logger = LogFactory.get_logger(self.__class__.__name__)

        try:
            if isinstance(duration, (int, float)):
                self.duration = float(duration)
            elif isinstance(duration, str):
                unit = duration[-1].lower()
                value = float(duration[:-1])
                if unit == "s":
                    self.duration = value
                elif unit == "m":
                    self.duration = value * 60
                elif unit == "h":
                    self.duration = value * 3600
                else:
                    self.logger.error(f"Invalid wait unit '{unit}'. Use 's', 'm', or 'h'.")
                    raise DSLError("Invalid wait unit. Use 's', 'm', or 'h'.")
            else:
                self.logger.error(
                    f"Wait value must be numeric or a string with a unit. Got: {type(duration)}"
                )
                raise TypeError("Wait value must be numeric or a string with a unit.")

            # Garantir que a duração seja válida (mínimo de espera)
            if self.duration < MIN_WAIT_LENGTH:
                self.logger.warning(
                    f"Wait duration {self.duration:.2f} is too short. Setting to minimum: {MIN_WAIT_LENGTH} seconds."
                )
                self.duration = MIN_WAIT_LENGTH

            self.logger.info(f"WaitInstruction created with duration: {self.duration:.2f} seconds")

        except ValueError as e:
            self.logger.error(f"Invalid wait value format: {duration}")
            raise DSLError(f"Invalid wait value '{duration}': {e}") from e

    def execute(self, context: Context) -> None:
        """
        Executa a instrução de espera, pausando a execução pelo período especificado.

        Este método utiliza a função `time.sleep` para pausar a execução por `self.duration`
        segundos. Durante a espera, mensagens de log são registradas para indicar o início e o
        término da operação.

        Parameters
        ----------
        context : Context
            Objeto que contém o estado e as variáveis do contexto de execução. Embora este método
            não modifique o contexto, ele o utiliza para manter a consistência na interface das
            instruções.

        Raises
        ------
        RuntimeError
            Se ocorrer um erro inesperado durante a execução da espera.
        """
        self.logger.info(f"Waiting for {self.duration:.2f} seconds...")

        try:
            time.sleep(self.duration)
            self.logger.debug("Wait completed successfully.")
        except Exception as e:
            self.logger.exception("Error during wait execution.")
            raise RuntimeError(f"Unexpected error during wait: {e}")
