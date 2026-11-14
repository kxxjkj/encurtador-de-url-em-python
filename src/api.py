"""Integração com a API pública do is.gd (não exige chave de cadastro)."""

import requests

ISGD_ENDPOINT = "https://is.gd/create.php"
DEFAULT_TIMEOUT = 10.0


class ShortenerError(Exception):
    """Erro base para falhas ao encurtar uma URL."""


class ConnectionFailedError(ShortenerError):
    """Falha de rede: sem internet, DNS ou timeout."""


class APIError(ShortenerError):
    """A API respondeu com erro ou com um formato inesperado."""


def shorten_url(url: str, timeout: float = DEFAULT_TIMEOUT) -> str:
    """Encurta uma URL usando a API do is.gd.

    Args:
        url: URL já validada a ser encurtada.
        timeout: Tempo máximo de espera pela resposta, em segundos.

    Returns:
        A URL encurtada.

    Raises:
        ConnectionFailedError: Se não for possível conectar à API.
        APIError: Se a API estiver fora do ar ou rejeitar a URL.
    """
    try:
        response = requests.get(
            ISGD_ENDPOINT,
            params={"format": "json", "url": url},
            timeout=timeout,
        )
    except requests.exceptions.Timeout as exc:
        raise ConnectionFailedError(
            "Tempo de resposta esgotado. Tente novamente em instantes."
        ) from exc
    except requests.exceptions.ConnectionError as exc:
        raise ConnectionFailedError(
            "Não foi possível conectar. Verifique sua conexão com a internet."
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise ConnectionFailedError(f"Erro na requisição: {exc}") from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise APIError(
            f"Resposta inválida da API (HTTP {response.status_code})."
        ) from exc

    if isinstance(data, dict) and data.get("shorturl"):
        return str(data["shorturl"])

    if response.status_code >= 500:
        raise APIError("A API está fora do ar no momento. Tente mais tarde.")

    message = data.get("errormessage") if isinstance(data, dict) else None
    raise APIError(message or "A API não retornou uma URL encurtada.")
