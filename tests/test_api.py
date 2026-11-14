"""Testes da integração com a API (requisições HTTP simuladas)."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from src.api import APIError, ConnectionFailedError, shorten_url


def _fake_response(status: int, payload: object) -> MagicMock:
    response = MagicMock()
    response.status_code = status
    response.json.return_value = payload
    return response


@patch("src.api.requests.get")
def test_shorten_success(mock_get: MagicMock) -> None:
    mock_get.return_value = _fake_response(200, {"shorturl": "https://is.gd/abc123"})

    assert shorten_url("https://exemplo.com/longa") == "https://is.gd/abc123"
    _, kwargs = mock_get.call_args
    assert kwargs["params"] == {"format": "json", "url": "https://exemplo.com/longa"}


@patch("src.api.requests.get")
def test_api_error_message(mock_get: MagicMock) -> None:
    mock_get.return_value = _fake_response(
        400, {"errorcode": 1, "errormessage": "Please enter a valid URL"}
    )
    with pytest.raises(APIError, match="valid URL"):
        shorten_url("https://exemplo.com")


@patch("src.api.requests.get")
def test_api_down(mock_get: MagicMock) -> None:
    mock_get.return_value = _fake_response(503, {})
    with pytest.raises(APIError, match="fora do ar"):
        shorten_url("https://exemplo.com")


@patch("src.api.requests.get")
def test_invalid_json(mock_get: MagicMock) -> None:
    response = _fake_response(200, None)
    response.json.side_effect = ValueError("no json")
    mock_get.return_value = response
    with pytest.raises(APIError, match="inválida"):
        shorten_url("https://exemplo.com")


@pytest.mark.parametrize(
    "exception",
    [
        requests.exceptions.ConnectionError(),
        requests.exceptions.Timeout(),
        requests.exceptions.RequestException(),
    ],
)
@patch("src.api.requests.get")
def test_network_failures(mock_get: MagicMock, exception: Exception) -> None:
    mock_get.side_effect = exception
    with pytest.raises(ConnectionFailedError):
        shorten_url("https://exemplo.com")
