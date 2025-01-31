"""Test ImperiumEngine."""

import imperiumengine


def test_import() -> None:
    """Test that the package can be imported."""
    assert isinstance(imperiumengine.__name__, str)
