import pytest
from project import normalize_name, normalize_email

def test_normalize_name():
    assert normalize_name("JOSE VIEIRA") == "Jose Vieira"
    assert normalize_name("   john peter   ") == "John Peter"

def test_normalize_name_empty():
    with pytest.raises(ValueError, match="empty name"):
        normalize_name("")
    with pytest.raises(ValueError, match="empty name"):
        normalize_name(" ")

def test_normalize_email():
    assert normalize_email("JOSE@GMAIL.COM") == "jose@gmail.com"
    assert normalize_email("   johnptr@gmail.com   ") == "johnptr@gmail.com"
    assert normalize_email("jose.vieira@gmail.com") == "jose.vieira@gmail.com"
    assert normalize_email("jose.vieira@company.com.br") == "jose.vieira@company.com.br"

def test_normalize_email_errors():
    with pytest.raises(ValueError, match="invalid email"):
        normalize_email("josevieira.com")
    with pytest.raises(ValueError, match="invalid email"):
        normalize_email("josevieira@gmail")
    with pytest.raises(ValueError, match="invalid email"):
        normalize_email("josevieira@gmail.com  xyz")
