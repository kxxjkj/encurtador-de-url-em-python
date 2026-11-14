"""Testes de integração da CLI (API e clipboard simulados)."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from src.api import ConnectionFailedError
from src.cli import app
from src.history import HISTORY_ENV_VAR, load_history

runner = CliRunner()
ENV = {"COLUMNS": "200"}


@pytest.fixture(autouse=True)
def history_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "history.json"
    monkeypatch.setenv(HISTORY_ENV_VAR, str(path))
    return path


@patch("src.cli.copy_to_clipboard", return_value=True)
@patch("src.cli.shorten_url", return_value="https://is.gd/abc")
def test_shorten_success(mock_shorten: MagicMock, mock_copy: MagicMock) -> None:
    result = runner.invoke(app, ["shorten", "exemplo.com/pagina"], env=ENV)

    assert result.exit_code == 0
    assert "https://is.gd/abc" in result.output
    mock_shorten.assert_called_once_with("https://exemplo.com/pagina")
    mock_copy.assert_called_once_with("https://is.gd/abc")
    assert len(load_history()) == 1


@patch("src.cli.shorten_url")
def test_shorten_invalid_url(mock_shorten: MagicMock) -> None:
    result = runner.invoke(app, ["shorten", "isso nao é url"], env=ENV)

    assert result.exit_code == 1
    assert "URL inválida" in result.output
    mock_shorten.assert_not_called()


@patch("src.cli.shorten_url", side_effect=ConnectionFailedError("Sem internet"))
def test_shorten_network_error(_: MagicMock) -> None:
    result = runner.invoke(app, ["shorten", "https://exemplo.com"], env=ENV)

    assert result.exit_code == 1
    assert "Sem internet" in result.output
    assert load_history() == []


@patch("src.cli.copy_to_clipboard")
@patch("src.cli.shorten_url", return_value="https://is.gd/abc")
def test_no_copy_flag(_: MagicMock, mock_copy: MagicMock) -> None:
    result = runner.invoke(app, ["shorten", "https://exemplo.com", "--no-copy"], env=ENV)

    assert result.exit_code == 0
    mock_copy.assert_not_called()


def test_history_empty() -> None:
    result = runner.invoke(app, ["history"], env=ENV)
    assert result.exit_code == 0
    assert "Nenhum link" in result.output


@patch("src.cli.copy_to_clipboard", return_value=True)
@patch("src.cli.shorten_url", return_value="https://is.gd/abc")
def test_history_table(_: MagicMock, __: MagicMock) -> None:
    runner.invoke(app, ["shorten", "https://exemplo.com/x"], env=ENV)
    result = runner.invoke(app, ["history"], env=ENV)

    assert result.exit_code == 0
    assert "https://exemplo.com/x" in result.output
    assert "https://is.gd/abc" in result.output
