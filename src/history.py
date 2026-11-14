"""Gerenciamento do histórico local de links encurtados (arquivo JSON)."""

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

HISTORY_ENV_VAR = "ENCURTADOR_HISTORY_FILE"


class HistoryError(Exception):
    """Falha ao ler ou gravar o arquivo de histórico."""


@dataclass(frozen=True)
class HistoryEntry:
    """Um registro do histórico.

    Attributes:
        original_url: URL original informada pelo usuário.
        short_url: URL encurtada retornada pela API.
        created_at: Data/hora de criação em ISO 8601 (UTC).
    """

    original_url: str
    short_url: str
    created_at: str


def get_history_path() -> Path:
    """Retorna o caminho do arquivo de histórico.

    Pode ser sobrescrito pela variável de ambiente ``ENCURTADOR_HISTORY_FILE``.
    Por padrão usa ``~/.encurtador-url/history.json``.
    """
    custom = os.environ.get(HISTORY_ENV_VAR)
    if custom:
        return Path(custom).expanduser()
    return Path.home() / ".encurtador-url" / "history.json"


def load_history() -> list[HistoryEntry]:
    """Carrega todas as entradas do histórico.

    Returns:
        Lista de entradas, da mais antiga para a mais recente. Lista vazia se
        o arquivo ainda não existir.

    Raises:
        HistoryError: Se o arquivo estiver corrompido ou ilegível.
    """
    path = get_history_path()
    if not path.exists():
        return []

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return [HistoryEntry(**item) for item in raw]
    except (OSError, json.JSONDecodeError, TypeError) as exc:
        raise HistoryError(f"Não foi possível ler o histórico em {path}: {exc}") from exc


def _save_history(entries: list[HistoryEntry]) -> None:
    """Grava a lista de entradas no arquivo de histórico."""
    path = get_history_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = [asdict(entry) for entry in entries]
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except OSError as exc:
        raise HistoryError(f"Não foi possível salvar o histórico: {exc}") from exc


def add_entry(original_url: str, short_url: str) -> HistoryEntry:
    """Adiciona um novo registro ao histórico.

    Args:
        original_url: URL original.
        short_url: URL encurtada.

    Returns:
        A entrada criada.

    Raises:
        HistoryError: Se não for possível ler ou gravar o arquivo.
    """
    entry = HistoryEntry(
        original_url=original_url,
        short_url=short_url,
        created_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )
    entries = load_history()
    entries.append(entry)
    _save_history(entries)
    return entry


def clear_history() -> int:
    """Apaga todo o histórico.

    Returns:
        Quantidade de registros removidos.
    """
    removed = len(load_history())
    _save_history([])
    return removed
