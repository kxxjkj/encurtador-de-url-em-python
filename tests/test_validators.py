"""Testes da validação de URLs."""

import pytest

from src.validators import InvalidURLError, normalize_url


@pytest.mark.parametrize(
    "url, expected",
    [
        ("https://www.python.org/downloads/", "https://www.python.org/downloads/"),
        ("http://exemplo.com.br/a?b=1#c", "http://exemplo.com.br/a?b=1#c"),
        ("github.com/user/repo", "https://github.com/user/repo"),
        ("  https://exemplo.com  ", "https://exemplo.com"),
        ("http://192.168.0.1:8080/x", "http://192.168.0.1:8080/x"),
    ],
)
def test_valid_urls(url: str, expected: str) -> None:
    assert normalize_url(url) == expected


@pytest.mark.parametrize(
    "url",
    [
        "",
        "   ",
        "ftp://exemplo.com",
        "http://",
        "https://localhost",
        "https://-invalido.com",
        "texto com espaços.com",
        "https://exemplo.com:abc",
        "https://exemplo.123",
    ],
)
def test_invalid_urls(url: str) -> None:
    with pytest.raises(InvalidURLError):
        normalize_url(url)
