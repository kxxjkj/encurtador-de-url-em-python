"""Validação e normalização de URLs."""

import ipaddress
import re
from urllib.parse import urlparse

_LABEL_RE = re.compile(r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)$")
_ALLOWED_SCHEMES = {"http", "https"}


class InvalidURLError(ValueError):
    """Lançada quando a URL informada não possui um formato válido."""


def normalize_url(url: str) -> str:
    """Valida uma URL e a devolve normalizada.

    Se o usuário não informar o esquema (ex.: ``google.com``), ``https://``
    é adicionado automaticamente.

    Args:
        url: URL digitada pelo usuário.

    Returns:
        A URL válida, já com esquema.

    Raises:
        InvalidURLError: Se a URL estiver vazia, tiver espaços, esquema
            diferente de http/https ou um domínio inválido.
    """
    candidate = url.strip()
    if not candidate:
        raise InvalidURLError("A URL não pode ser vazia.")
    if re.search(r"\s", candidate):
        raise InvalidURLError("A URL não pode conter espaços.")

    if "://" not in candidate:
        candidate = f"https://{candidate}"

    parsed = urlparse(candidate)
    if parsed.scheme.lower() not in _ALLOWED_SCHEMES:
        raise InvalidURLError(
            f"Esquema '{parsed.scheme}' não suportado. Use http ou https."
        )

    try:
        host = parsed.hostname
        _ = parsed.port  # dispara ValueError se a porta for inválida
    except ValueError as exc:
        raise InvalidURLError("A URL contém uma porta ou host inválido.") from exc

    if not host:
        raise InvalidURLError("A URL não possui um domínio válido.")

    if not _is_valid_host(host):
        raise InvalidURLError(f"Domínio inválido: '{host}'.")

    return candidate


def _is_valid_host(host: str) -> bool:
    """Verifica se ``host`` é um IP válido ou um domínio bem formado."""
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        pass

    try:
        ascii_host = host.encode("idna").decode("ascii")
    except UnicodeError:
        return False

    labels = ascii_host.split(".")
    if len(labels) < 2:
        return False
    if not all(_LABEL_RE.match(label) for label in labels):
        return False
    return not labels[-1].isdigit()
