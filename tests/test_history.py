"""Testes do gerenciamento de histórico."""

from pathlib import Path

import pytest

from src.history import (
    HISTORY_ENV_VAR,
    HistoryError,
    add_entry,
    clear_history,
    load_history,
)


@pytest.fixture(autouse=True)
def history_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Isola o histórico em um arquivo temporário."""
    path = tmp_path / "history.json"
    monkeypatch.setenv(HISTORY_ENV_VAR, str(path))
    return path


def test_empty_history() -> None:
    assert load_history() == []


def test_add_and_load() -> None:
    add_entry("https://exemplo.com/a", "https://is.gd/a")
    add_entry("https://exemplo.com/b", "https://is.gd/b")

    entries = load_history()
    assert [e.short_url for e in entries] == ["https://is.gd/a", "https://is.gd/b"]
    assert entries[0].original_url == "https://exemplo.com/a"
    assert entries[0].created_at


def test_clear() -> None:
    add_entry("https://exemplo.com", "https://is.gd/x")
    assert clear_history() == 1
    assert load_history() == []


def test_corrupted_file(history_file: Path) -> None:
    history_file.write_text("{ isso não é json", encoding="utf-8")
    with pytest.raises(HistoryError):
        load_history()
