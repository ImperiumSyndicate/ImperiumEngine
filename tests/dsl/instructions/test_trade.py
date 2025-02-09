from imperiumengine.dsl.context import Context
from imperiumengine.dsl.instructions.trade import TradeInstruction


def test_trade_execution_new_trades():
    """
    Testa se a execução de uma TradeInstruction adiciona os dados do trade
    ao contexto quando a chave "trades" não existe.

    Cria um contexto novo, executa a instrução de trade e verifica se a chave "trades"
    é criada com uma lista contendo o trade.
    """
    context = Context()  # O construtor já inicializa context.variables como {}
    trade_data = {"action": "buy", "symbol": "AAPL", "quantity": 100}
    trade_instr = TradeInstruction(trade_data)
    trade_instr.execute(context)

    # Verifica se a chave "trades" foi criada e contém o trade_data
    assert "trades" in context.variables
    assert isinstance(context.variables["trades"], list)
    assert context.variables["trades"] == [trade_data]


def test_trade_execution_append_existing():
    """
    Testa se a execução de uma TradeInstruction acrescenta os dados do trade
    à lista já existente no contexto.

    Inicialmente, preenche o contexto com um trade já registrado e, em seguida,
    executa uma nova instrução de trade. Verifica se a lista resultante contém ambos os trades.
    """
    context = Context()
    # Pre-popula o contexto com um trade existente
    context.variables["trades"] = [{"action": "sell", "symbol": "GOOG", "quantity": 50}]
    trade_data = {"action": "buy", "symbol": "AAPL", "quantity": 100}
    trade_instr = TradeInstruction(trade_data)
    trade_instr.execute(context)

    expected = [{"action": "sell", "symbol": "GOOG", "quantity": 50}, trade_data]
    assert context.variables["trades"] == expected


def test_trade_no_side_effects():
    """
    Testa que a execução de uma TradeInstruction não modifica outras variáveis do contexto.

    Adiciona uma chave "other" ao contexto antes de executar a instrução e verifica que essa
    variável permanece inalterada após a execução.
    """
    context = Context()
    context.variables["other"] = "value"
    trade_data = {"action": "buy", "symbol": "AAPL", "quantity": 100}
    trade_instr = TradeInstruction(trade_data)
    trade_instr.execute(context)

    # Verifica que a variável "other" não foi alterada
    assert context.variables["other"] == "value"
