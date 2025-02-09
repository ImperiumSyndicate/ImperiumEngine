from imperiumengine.dsl.validators import StrategyValidator


def test_valid_instructions():
    """
    Testa uma sequência de instruções válida, que deve resultar em validação bem-sucedida (is_valid True)
    e sem erros acumulados.
    """
    instructions = [
        {"if": "x > 0"},
        {"operation": "x += 1"},
        {"end": True},
        {"trade": {"action": "buy", "symbol": "AAPL", "quantity": 10}},
    ]
    validator = StrategyValidator(instructions)
    is_valid, errs = validator.validate()
    assert is_valid is True, "A estratégia deve ser válida."
    assert errs == [], "Não deve haver erros acumulados para uma estratégia válida."


def test_invalid_if_condition():
    """
    Testa o caso em que a instrução 'if' possui condição com tipo inválido (não-string).
    Deve acumular um erro informando que a condição precisa ser uma string.
    """
    instructions = [{"if": 123}]
    validator = StrategyValidator(instructions)
    is_valid, errs = validator.validate()
    assert is_valid is False, "A estratégia deve ser inválida se a condição não for uma string."
    assert any("condition must be a string" in err for err in errs), (
        "Deve registrar erro quanto ao tipo da condição."
    )


def test_unexpected_end():
    """
    Testa o caso em que há uma instrução 'end' sem um correspondente 'if'.
    Deve acumular um erro de 'Unexpected 'end''.
    """
    instructions = [{"end": True}]
    validator = StrategyValidator(instructions)
    is_valid, errs = validator.validate()
    assert is_valid is False, "A estratégia deve ser inválida se houver um 'end' sem 'if'."
    assert any("Unexpected 'end'" in err for err in errs), (
        "Deve registrar erro quanto ao 'end' inesperado."
    )


def test_indicator_missing_keys():
    """
    Testa a validação de uma instrução 'indicator' onde faltam chaves obrigatórias.
    Para um indicador que não seja MACD, as chaves 'period', 'source' e 'var' são obrigatórias.
    """
    instructions = [{"indicator": {"name": "SMA"}}]
    validator = StrategyValidator(instructions)
    is_valid, errs = validator.validate()
    assert is_valid is False, (
        "A estratégia deve ser inválida se faltarem chaves obrigatórias no indicador."
    )
    # Verifica se os erros mencionam as chaves faltantes
    assert any("missing key 'period'" in err for err in errs), (
        "Deve haver erro quanto à chave 'period' faltante."
    )
    assert any("missing key 'source'" in err for err in errs), (
        "Deve haver erro quanto à chave 'source' faltante."
    )
    assert any("missing key 'var'" in err for err in errs), (
        "Deve haver erro quanto à chave 'var' faltante."
    )


def test_trade_invalid_action():
    """
    Testa a validação de uma instrução 'trade' com ação inválida (não 'buy' nem 'sell').
    """
    instructions = [{"trade": {"action": "hold", "symbol": "AAPL", "quantity": 10}}]
    validator = StrategyValidator(instructions)
    is_valid, errs = validator.validate()
    assert is_valid is False, "A estratégia deve ser inválida para ação de trade não permitida."
    assert any("invalid action" in err for err in errs), (
        "Deve registrar erro quanto à ação de trade inválida."
    )


def test_wait_invalid_format():
    """
    Testa a validação de uma instrução 'wait' com formato inválido (string sem unidade válida).
    """
    instructions = [{"wait": "abc"}]
    validator = StrategyValidator(instructions)
    is_valid, errs = validator.validate()
    assert is_valid is False, (
        "A estratégia deve ser inválida se o formato de espera estiver incorreto."
    )
    assert any("invalid format" in err for err in errs), (
        "Deve registrar erro quanto ao formato inválido do 'wait'."
    )


def test_wait_numeric_valid():
    """
    Testa a validação de uma instrução 'wait' com valor numérico válido.
    """
    instructions = [{"wait": 5}]
    validator = StrategyValidator(instructions)
    is_valid, errs = validator.validate()
    assert is_valid is True, "A instrução de espera numérica válida não deve gerar erros."
    assert errs == [], "Nenhum erro deve ser acumulado para uma espera numérica válida."


def test_operation_invalid_code():
    """
    Testa a validação de uma instrução 'operation' com código de tipo inválido (não-string).
    """
    instructions = [{"operation": 123}]
    validator = StrategyValidator(instructions)
    is_valid, errs = validator.validate()
    assert is_valid is False, "A operação deve ser inválida se o código não for uma string."
    assert any("must be a string" in err for err in errs), (
        "Deve registrar erro quanto ao tipo do código da operação."
    )


def test_operation_valid_code():
    """
    Testa a validação de uma instrução 'operation' com código válido.
    """
    instructions = [{"operation": "x = 1"}]
    validator = StrategyValidator(instructions)
    is_valid, errs = validator.validate()
    assert is_valid is True, "A operação válida não deve gerar erros."
    assert errs == [], "Nenhum erro deve ser acumulado para uma operação com código válido."


def test_if_invalid_expression():
    """
    Testa a validação de uma instrução 'if' cuja condição é uma string, mas não uma expressão Python válida.
    """
    instructions = [{"if": "x >"}]
    validator = StrategyValidator(instructions)
    is_valid, errs = validator.validate()
    assert is_valid is False, "A estratégia deve ser inválida se a expressão 'if' não for válida."
    assert any("Error in condition" in err for err in errs), (
        "Deve registrar erro na avaliação da condição do 'if'."
    )


def test_unknown_instruction():
    """
    Testa a situação em que uma instrução com uma chave não reconhecida é ignorada.
    Essa instrução deve ser ignorada sem causar erro, mantendo a estratégia válida.
    """
    instructions = [{"unknown": "something"}]
    validator = StrategyValidator(instructions)
    is_valid, errs = validator.validate()
    assert is_valid is True, (
        "Instruções desconhecidas devem ser ignoradas, mantendo a estratégia válida."
    )
    assert errs == [], "Nenhum erro deve ser acumulado para instruções desconhecidas."
