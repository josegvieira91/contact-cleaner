import pytest
from project import normalize_name

def test_normalize_name():
    assert normalize_name("JOSE VIEIRA") == "Jose Vieira"
    assert normalize_name("   john peter   ") == "John Peter"

def test_normalize_name_empty():
    with pytest.raises(ValueError, match="empty name"):
        normalize_name("")
    with pytest.raises(ValueError, match="empty name"):
        normalize_name(" ")