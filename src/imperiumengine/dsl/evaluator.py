import ast
import re
from typing import Any, ClassVar

from imperiumengine.dsl.exceptions import DSLError


class SafeEvaluator(ast.NodeVisitor):
    """
    Avalia expressões de uma DSL de forma segura utilizando uma AST restrita.

    Esta classe percorre a árvore sintática abstrata (AST) gerada a partir de uma expressão e
    avalia os nós permitidos, garantindo que somente operações seguras sejam executadas. Operações
    não permitidas ou nós inesperados geram uma exceção `DSLError`.

    A classe permite operações aritméticas simples, operações unárias, operações booleanas, comparações,
    além de chamadas a funções permitidas. As funções autorizadas estão definidas na variável de classe
    `ALLOWED_FUNCTIONS`.

    Attributes
    ----------
    ALLOWED_FUNCTIONS : ClassVar[set[str]]
        Conjunto de nomes de funções que são permitidas nas expressões. Valores permitidos:
        {"implies", "iff", "xor", "nand", "nor"}.
    context : dict[str, Any]
        Dicionário que representa o contexto de avaliação, contendo variáveis e funções disponíveis.

    Parameters
    ----------
    context : dict[str, Any]
        Dicionário contendo as variáveis e funções que poderão ser utilizadas durante a avaliação.

    Examples
    --------
    >>> # Exemplo simples de avaliação segura:
    >>> contexto = {"x": 10, "y": 5}
    >>> evaluator = SafeEvaluator(contexto)
    >>> import ast
    >>> node = ast.parse("x + y", mode="eval")
    >>> evaluator.visit(node.body)
    15
    """

    ALLOWED_FUNCTIONS: ClassVar[set[str]] = {"implies", "iff", "xor", "nand", "nor"}

    def __init__(self, context: dict[str, Any]) -> None:
        self.context = context

    def visit_binop(self, node: ast.BinOp) -> Any:
        """
        Avalia uma operação binária (ex.: adição, subtração).

        Parameters
        ----------
        node : ast.BinOp
            Nó da AST que representa uma operação binária.

        Returns
        -------
        Any
            Resultado da operação binária avaliada.

        Raises
        ------
        DSLError
            Se o operador binário não for suportado.
        """
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        if isinstance(node.op, ast.Mod):
            return left % right
        if isinstance(node.op, ast.Pow):
            return left**right
        raise DSLError(f"Binary operator {type(node.op).__name__} is not supported.")

    visit_BinOp = visit_binop

    def visit_unaryop(self, node: ast.UnaryOp) -> Any:
        """
        Avalia uma operação unária (ex.: negação).

        Parameters
        ----------
        node : ast.UnaryOp
            Nó da AST que representa uma operação unária.

        Returns
        -------
        Any
            Resultado da operação unária avaliada.

        Raises
        ------
        DSLError
            Se o operador unário não for suportado.
        """
        operand = self.visit(node.operand)
        if isinstance(node.op, ast.UAdd):
            return +operand
        if isinstance(node.op, ast.USub):
            return -operand
        if isinstance(node.op, ast.Not):
            return not operand
        raise DSLError(f"Unary operator {type(node.op).__name__} is not supported.")

    visit_UnaryOp = visit_unaryop

    def visit_num(self, node: ast.Num) -> Any:
        """
        Retorna o valor numérico de um nó antigo (para versões de Python anteriores a 3.8).

        Parameters
        ----------
        node : ast.Num
            Nó que contém um valor numérico.

        Returns
        -------
        Any
            Valor numérico armazenado em node.n.
        """
        return node.n

    visit_Num = visit_num

    def visit_constant(self, node: ast.Constant) -> Any:
        """
        Retorna o valor de um nó constante (utilizado em Python 3.8+).

        Parameters
        ----------
        node : ast.Constant
            Nó que contém um valor constante.

        Returns
        -------
        Any
            Valor constante armazenado em node.value.
        """
        return node.value

    visit_Constant = visit_constant

    def visit_name(self, node: ast.Name) -> Any:
        """
        Recupera o valor de uma variável a partir do contexto.

        Parameters
        ----------
        node : ast.Name
            Nó que representa uma variável.

        Returns
        -------
        Any
            Valor da variável obtido a partir do contexto.

        Raises
        ------
        DSLError
            Se a variável não estiver presente no contexto.
        """
        if node.id in self.context:
            return self.context[node.id]
        raise DSLError(f"Variable '{node.id}' not found in context.")

    visit_Name = visit_name

    def visit_boolop(self, node: ast.BoolOp) -> Any:
        """
        Avalia operações booleanas (AND, OR).

        Parameters
        ----------
        node : ast.BoolOp
            Nó que representa uma operação booleana.

        Returns
        -------
        Any
            Resultado da operação booleana.

        Raises
        ------
        DSLError
            Se o operador booleano não for suportado.
        """
        if isinstance(node.op, ast.And):
            result = True
            for value in node.values:
                result = result and self.visit(value)
                if not result:
                    return False
            return True
        if isinstance(node.op, ast.Or):
            result = False
            for value in node.values:
                result = result or self.visit(value)
                if result:
                    return True
            return False
        raise DSLError("Boolean operator not supported.")

    visit_BoolOp = visit_boolop

    def visit_compare(self, node: ast.Compare) -> Any:
        """
        Avalia expressões de comparação (ex.: >, <, ==).

        Parameters
        ----------
        node : ast.Compare
            Nó que representa uma comparação.

        Returns
        -------
        Any
            Valor booleano que resulta da comparação.

        Raises
        ------
        DSLError
            Se algum operador de comparação não for suportado.
        """
        left = self.visit(node.left)
        for op, comparator in zip(node.ops, node.comparators, strict=False):
            right = self.visit(comparator)
            if isinstance(op, ast.Gt):
                if left <= right:
                    return False
            elif isinstance(op, ast.GtE):
                if left < right:
                    return False
            elif isinstance(op, ast.Lt):
                if left >= right:
                    return False
            elif isinstance(op, ast.LtE):
                if left > right:
                    return False
            elif isinstance(op, ast.Eq):
                if left != right:
                    return False
            elif isinstance(op, ast.NotEq):
                if left == right:
                    return False
            else:
                raise DSLError(f"Comparison operator {type(op).__name__} is not supported.")
            left = right
        return True

    visit_Compare = visit_compare

    def visit_call(self, node: ast.Call) -> Any:
        """
        Avalia uma chamada de função.

        Somente chamadas a funções presentes em `ALLOWED_FUNCTIONS` são permitidas.
        Os argumentos e palavras-chave da chamada são avaliados recursivamente.

        Parameters
        ----------
        node : ast.Call
            Nó que representa uma chamada de função.

        Returns
        -------
        Any
            Resultado da chamada da função.

        Raises
        ------
        DSLError
            Se a função chamada não for permitida ou não estiver presente no contexto, ou se a
            chamada não for uma chamada simples.
        """
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name not in self.ALLOWED_FUNCTIONS:
                raise DSLError(f"Function call '{func_name}' is not permitted.")
            args = [self.visit(arg) for arg in node.args]
            kwargs = {kw.arg: self.visit(kw.value) for kw in node.keywords if kw.arg is not None}
            if func_name not in self.context:
                raise DSLError(f"Function '{func_name}' not found in context.")
            func = self.context[func_name]
            return func(*args, **kwargs)
        raise DSLError("Only simple function calls are allowed.")

    visit_Call = visit_call

    def generic_visit(self, node: ast.AST) -> Any:
        """
        Método genérico de visita que impede a avaliação de nós não permitidos.

        Parameters
        ----------
        node : ast.AST
            Nó da AST que não possui um método de visita específico.

        Raises
        ------
        DSLError
            Sempre levanta uma exceção indicando que o nó não é permitido.
        """
        raise DSLError(f"AST node {type(node).__name__} is not permitted in safe expressions.")


def safe_eval_expr(expr: str, context: dict[str, Any]) -> Any:
    """
    Avalia de forma segura uma expressão em uma DSL utilizando uma AST restrita.

    Esta função substitui operadores especiais por suas equivalentes em forma de chamada de função.
    Em seguida, cria um contexto local que inclui funções permitidas para operações lógicas e avalia a
    expressão utilizando a classe `SafeEvaluator`.

    Parameters
    ----------
    expr : str
        A expressão a ser avaliada. Pode conter operadores especiais que serão convertidos.
    context : dict[str, Any]
        Dicionário com variáveis e funções disponíveis para a avaliação da expressão.

    Returns
    -------
    Any
        Resultado da avaliação da expressão.

    Raises
    ------
    DSLError
        Se ocorrer algum erro durante a análise ou avaliação segura da expressão.
    """
    # Usa regex para converter operadores especiais em chamadas de função.
    expr = re.sub(r"(\S+)\s*→\s*(\S+)", r"implies(\1, \2)", expr)
    expr = re.sub(r"(\S+)\s*↔\s*(\S+)", r"iff(\1, \2)", expr)
    expr = re.sub(r"(\S+)\s*⊕\s*(\S+)", r"xor(\1, \2)", expr)
    expr = re.sub(r"(\S+)\s*↑\s*(\S+)", r"nand(\1, \2)", expr)
    expr = re.sub(r"(\S+)\s*↓\s*(\S+)", r"nor(\1, \2)", expr)

    local_context = dict(context)
    local_context["implies"] = lambda x, y: (not x) or y
    local_context["iff"] = lambda x, y: (x and y) or ((not x) and (not y))
    local_context["xor"] = lambda x, y: (x and (not y)) or ((not x) and y)
    local_context["nand"] = lambda x, y: not (x and y)
    local_context["nor"] = lambda x, y: not (x or y)
    try:
        node = ast.parse(expr, mode="eval")
        evaluator = SafeEvaluator(local_context)
        return evaluator.visit(node.body)
    except Exception as e:
        raise DSLError(f"Error in safe evaluation of expression '{expr}': {e}") from e


def safe_exec_statement(statement: str, context: dict[str, Any]) -> None:
    """
    Executa de forma segura uma única instrução definida por uma string.

    Esta função permite apenas instruções simples, como atribuições simples a uma variável ou
    chamadas de função restritas (por exemplo, a função `print`). Instruções com mais de um
    comando ou estruturas não permitidas geram uma exceção `DSLError`.

    Parameters
    ----------
    statement : str
        A instrução a ser executada. Exemplos: "x = 5" ou "print(x)".
    context : dict[str, Any]
        Dicionário contendo as variáveis (e funções) que poderão ser modificadas ou utilizadas
        durante a execução da instrução.

    Returns
    -------
    None

    Raises
    ------
    DSLError
        Se a instrução não estiver no formato permitido, se houver mais de uma instrução, ou se
        a instrução contiver elementos não permitidos.

    Examples
    --------
    >>> contexto = {"x": 10}
    >>> safe_exec_statement("x = x + 5", contexto)
    >>> contexto["x"]
    15
    >>> # Apenas chamadas à função print são permitidas:
    >>> safe_exec_statement("print(x)", contexto)
    15
    """
    try:
        tree = ast.parse(statement, mode="exec")
    except Exception as e:
        raise DSLError(f"Error parsing statement '{statement}': {e}") from e

    if len(tree.body) != 1:
        raise DSLError("Only one statement is permitted.")

    node = tree.body[0]
    evaluator = SafeEvaluator(context)

    if isinstance(node, ast.Assign):
        if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
            raise DSLError("Assignment target must be a single variable.")
        var_name = node.targets[0].id
        value = evaluator.visit(node.value)
        context[var_name] = value
    elif isinstance(node, ast.Expr):
        expr = node.value
        if isinstance(expr, ast.Call):
            if isinstance(expr.func, ast.Name) and expr.func.id == "print":
                args = [evaluator.visit(arg) for arg in expr.args]
                kwargs = {
                    kw.arg: evaluator.visit(kw.value) for kw in expr.keywords if kw.arg is not None
                }
                print(*args, **kwargs)
            else:
                raise DSLError("Only 'print' function calls are permitted.")
        else:
            raise DSLError("Only function calls are permitted in expressions.")
    else:
        raise DSLError("Only simple assignments or permitted function calls are allowed.")
