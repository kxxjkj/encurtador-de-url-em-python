"""Interface de linha de comando (CLI) do encurtador de URLs."""

from datetime import datetime

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src import __version__
from src.api import ShortenerError, shorten_url
from src.clipboard import copy_to_clipboard
from src.history import HistoryError, add_entry, clear_history, load_history
from src.validators import InvalidURLError, normalize_url

app = typer.Typer(
    name="encurtar",
    help="✂️  Encurtador de URLs via terminal, com histórico e clipboard.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()
err_console = Console(stderr=True)


def _print_error(title: str, message: str) -> None:
    """Exibe uma mensagem de erro formatada no stderr."""
    err_console.print(
        Panel(message, title=f"❌ {title}", border_style="red", expand=False)
    )


def _format_date(iso_date: str) -> str:
    """Converte uma data ISO 8601 (UTC) para o fuso local, formato BR."""
    try:
        return datetime.fromisoformat(iso_date).astimezone().strftime("%d/%m/%Y %H:%M")
    except ValueError:
        return iso_date


def _version_callback(value: bool) -> None:
    """Mostra a versão e encerra o programa."""
    if value:
        console.print(f"encurtar v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        callback=_version_callback,
        is_eager=True,
        help="Mostra a versão e sai.",
    ),
) -> None:
    """Encurtador de URLs via terminal."""


@app.command()
def shorten(
    url: str = typer.Argument(..., help="URL longa que será encurtada."),
    no_copy: bool = typer.Option(
        False, "--no-copy", help="Não copia o resultado para a área de transferência."
    ),
) -> None:
    """Encurta uma URL, salva no histórico e copia o resultado."""
    try:
        clean_url = normalize_url(url)
    except InvalidURLError as exc:
        _print_error("URL inválida", str(exc))
        raise typer.Exit(code=1) from exc

    try:
        with console.status("[cyan]Encurtando link...[/cyan]"):
            short_url = shorten_url(clean_url)
    except ShortenerError as exc:
        _print_error("Falha ao encurtar", str(exc))
        raise typer.Exit(code=1) from exc

    try:
        add_entry(clean_url, short_url)
    except HistoryError as exc:
        console.print(f"[yellow]⚠️  Link criado, mas o histórico falhou: {exc}[/yellow]")

    copied = False if no_copy else copy_to_clipboard(short_url)

    footer = "[green]📋 Copiado para a área de transferência![/green]"
    if no_copy:
        footer = "[dim]Cópia para a área de transferência desativada.[/dim]"
    elif not copied:
        footer = "[yellow]⚠️  Não foi possível acessar a área de transferência.[/yellow]"

    console.print(
        Panel(
            f"[bold green]{short_url}[/bold green]\n\n{footer}",
            title="✅ Link encurtado",
            border_style="green",
            expand=False,
        )
    )


@app.command()
def history(
    limit: int = typer.Option(
        20, "--limit", "-n", min=1, help="Quantidade de registros mais recentes."
    ),
) -> None:
    """Lista o histórico de links encurtados em formato de tabela."""
    try:
        entries = load_history()
    except HistoryError as exc:
        _print_error("Erro no histórico", str(exc))
        raise typer.Exit(code=1) from exc

    if not entries:
        console.print("[yellow]Nenhum link encurtado ainda. Use `encurtar shorten <url>`.[/yellow]")
        return

    recent = list(reversed(entries))[:limit]
    table = Table(
        title="📜 Histórico de links", header_style="bold magenta", show_lines=True
    )
    table.add_column("#", justify="right", style="dim")
    table.add_column("Data", style="cyan", no_wrap=True)
    table.add_column("URL original", overflow="fold", max_width=50)
    table.add_column("URL encurtada", style="bold green", no_wrap=True)

    for index, entry in enumerate(recent, start=1):
        table.add_row(
            str(index),
            _format_date(entry.created_at),
            entry.original_url,
            entry.short_url,
        )

    console.print(table)
    console.print(f"[dim]Exibindo {len(recent)} de {len(entries)} registro(s).[/dim]")


@app.command()
def clear(
    yes: bool = typer.Option(False, "--yes", "-y", help="Não pede confirmação."),
) -> None:
    """Apaga todo o histórico local."""
    if not yes and not typer.confirm("Apagar todo o histórico?"):
        console.print("[dim]Operação cancelada.[/dim]")
        raise typer.Exit()

    try:
        removed = clear_history()
    except HistoryError as exc:
        _print_error("Erro no histórico", str(exc))
        raise typer.Exit(code=1) from exc

    console.print(f"[green]🗑️  {removed} registro(s) removido(s).[/green]")


if __name__ == "__main__":
    app()
