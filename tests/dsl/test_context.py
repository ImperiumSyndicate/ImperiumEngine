import pytest

from imperiumengine.dsl.context import Context


@pytest.fixture
def ctx() -> Context:
    """Fixture que retorna uma nova instância de Context para cada teste."""
    return Context()


def test_initial_variables_empty(ctx: Context):
    """Verifica se, ao ser instanciado, o contexto possui um dicionário vazio."""
    assert ctx.variables == {}, "Inicialmente, o dicionário de variáveis deve estar vazio."


def test_update_add_new_keys(ctx: Context):
    """Verifica se o método update adiciona corretamente novas chaves ao contexto."""
    data = {"a": 1, "b": 2}
    ctx.update(data)
    assert ctx.variables == data, (
        "Após a atualização, o contexto deve conter as chaves e valores fornecidos."
    )


def test_update_modify_existing_key(ctx: Context):
    """Verifica se o método update atualiza o valor de uma chave já existente."""
    ctx.update({"a": 1})
    ctx.update({"a": 2})
    assert ctx.variables["a"] == 2, "O valor da chave 'a' deve ser atualizado para 2."


def test_update_merge_dictionaries(ctx: Context):
    """Verifica se atualizações sucessivas realizam a fusão dos dicionários corretamente."""
    ctx.update({"a": 1, "b": 2})
    ctx.update({"b": 3, "c": 4})
    expected = {"a": 1, "b": 3, "c": 4}
    assert ctx.variables == expected, (
        "O contexto deve mesclar os dicionários, atualizando os valores das chaves existentes."
    )
