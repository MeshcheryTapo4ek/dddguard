from contextlib import contextmanager
from typing import Generator
import typer
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich import box

console = Console()


@contextmanager
def safe_execution(
    status_msg: str = "Processing...",
    spinner: str = "dots",
    error_title: str = "❌ Operation Failed",
) -> Generator[None, None, None]:
    """
    Unified UI wrapper for executing logic with a spinner and standardized error reporting.
    """
    try:
        with console.status(f"[bold blue]{status_msg}[/]", spinner=spinner):
            yield
    except typer.Exit:
        raise
    except Exception as e:
        console.print()
        panel = Panel(
            Align.center(f"[white]{str(e)}[/]"),
            title=f"[bold red]{error_title}[/]",
            border_style="red",
            box=box.ROUNDED,
            padding=(1, 2),
            expand=False,
        )
        console.print(panel)
        console.print()
        raise typer.Exit(1)
