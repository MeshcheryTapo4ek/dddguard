import sys
import traceback
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import typer
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.validator import EmptyInputValidator
from rich import box
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from dddguard.shared.helpers.generics import BaseDddError

from .themes import DEFAULT_THEME, GuardTheme


class Tui:
    """
    Unified Text User Interface Adapter.
    Centralizes all Rich and InquirerPy interactions.
    """

    def __init__(self):
        self._console = Console()
        self._theme = DEFAULT_THEME

    @property
    def console(self) -> Console:
        return self._console

    def set_theme(self, theme: GuardTheme) -> None:
        self._theme = theme

    # --- OUTPUT COMPONENTS ---

    def dashboard(
        self,
        title: str,
        data: dict[str, Any] | list[dict[str, Any]],
        subtitle: str = "",
        theme: GuardTheme | None = None,
    ) -> None:
        """
        Renders a standardized dashboard panel.
        Supports single column (Dict) or two-column split (List[Dict, Dict]).
        """
        active_theme = theme or self._theme
        color = active_theme.primary_color

        # Header
        grid = Table.grid(expand=True, padding=(0, 2))

        # Determine Layout
        if isinstance(data, list) and len(data) == 2:
            # Two Column Layout
            left_data, right_data = data

            # Left Table
            t1 = Table.grid(padding=(0, 2))
            t1.add_column(style="dim", justify="right", min_width=12)
            t1.add_column(style="bold white")
            for k, v in left_data.items():
                t1.add_row(f"{k}:", str(v))

            # Right Table
            t2 = Table.grid(padding=(0, 2))
            t2.add_column(style="dim", justify="right", min_width=12)
            t2.add_column(style=f"bold {color}")
            for k, v in right_data.items():
                t2.add_row(f"{k}:", str(v))

            # Combine in main grid
            grid.add_column(ratio=1)
            grid.add_column(ratio=1)
            grid.add_row(t1, t2)

        elif isinstance(data, dict):
            # Single Column Layout
            t = Table.grid(padding=(0, 2))
            t.add_column(style="dim", justify="right", min_width=15)
            t.add_column(style="bold white")
            for k, v in data.items():
                t.add_row(f"{k}:", str(v))

            grid.add_column(justify="center")
            grid.add_row(t)

        self._console.print(
            Panel(
                Align.center(grid),
                title=f"[bold {color}]{title}[/]",
                subtitle=f"[dim]{subtitle}[/]" if subtitle else None,
                subtitle_align="right",
                border_style=color,
                padding=(1, 2),
                expand=True,
            )
        )

    def success(self, title: str, details: dict[str, str] | None = None) -> None:
        self._render_status_panel(title, "green", details)

    def error(self, title: str, details: str | dict[str, str] | None = None) -> None:
        self._render_status_panel(title, "red", details)

    def warning(self, title: str, details: str | dict[str, str] | None = None) -> None:
        self._render_status_panel(title, "yellow", details)

    def _render_status_panel(
        self,
        title: str,
        color: str,
        details: str | dict[str, str] | None,
    ) -> None:
        from rich.align import Align
        from rich.console import RenderableType

        content: RenderableType = Text("")

        if details:
            if isinstance(details, str):
                content = Align.center(f"[{color}]{details}[/]")
            elif isinstance(details, dict):
                grid = Table.grid(padding=(0, 2))
                grid.add_column(style="dim", justify="right")
                grid.add_column(style="bold white")
                for k, v in details.items():
                    grid.add_row(f"{k}:", str(v))
                content = Align.center(grid)

        self._console.print()
        self._console.print(
            Panel(
                content,
                title=f"[bold {color}]{title}[/]",
                border_style=color,
                box=box.ROUNDED,
                padding=(1, 2),
                expand=False,
            )
        )
        self._console.print()

    # --- INPUT COMPONENTS ---

    def select(
        self,
        message: str | None,
        choices: list[Any],
        default: Any = None,
        theme: GuardTheme | None = None,
        use_fuzzy: bool = False,
        instruction: str = "(Use arrow keys)",
    ) -> Any:
        active_theme = theme or self._theme
        style = active_theme.get_style()
        msg_str = message or ""

        try:
            if use_fuzzy:
                return inquirer.fuzzy(
                    message=msg_str,
                    choices=choices,
                    default=default,
                    style=style,
                    qmark="🔍",
                    pointer="❯",
                    border=False,
                    instruction=instruction,
                    prompt="Filter: ",
                ).execute()
            return inquirer.select(
                message=msg_str,
                choices=choices,
                default=default,
                style=style,
                qmark="",
                amark="",
                pointer="❯",
                instruction=instruction,
            ).execute()
        except KeyboardInterrupt:
            return None

    def multiselect(
        self,
        message: str | None,
        choices: list[Any],
        theme: GuardTheme | None = None,
        instruction: str = "(Space to select)",
        use_fuzzy: bool = False,  # <--- Added Parameter
    ) -> list[Any] | None:
        active_theme = theme or self._theme
        msg_str = message or ""
        try:
            if use_fuzzy:
                return inquirer.fuzzy(
                    message=msg_str,
                    choices=choices,
                    multiselect=True,
                    style=active_theme.get_style(),
                    qmark="🔍",
                    pointer="❯",
                    marker="[x]",
                    border=False,
                    instruction=instruction,
                    prompt="Filter: ",
                    validate=lambda result: len(result) > 0 or "Pick at least one",
                ).execute()
            return inquirer.checkbox(
                message=msg_str,
                choices=choices,
                style=active_theme.get_style(),
                qmark="",
                pointer="❯",
                enabled_symbol="[x]",
                disabled_symbol="[ ]",
                instruction=instruction,
                validate=lambda result: len(result) > 0 or "Select at least one option",
            ).execute()
        except KeyboardInterrupt:
            return None

    def text(
        self,
        message: str,
        default: str = "",
        allow_empty: bool = False,
        theme: GuardTheme | None = None,
    ) -> str | None:
        active_theme = theme or self._theme
        try:
            return inquirer.text(
                message=message + ":",
                default=default,
                validate=EmptyInputValidator() if not allow_empty else None,
                style=active_theme.get_style(),
                qmark="📝",
                instruction="(Ctrl+C to cancel)",
            ).execute()
        except KeyboardInterrupt:
            return None

    def path(self, message: str = "Select directory", default: str = ".") -> Path | None:
        """
        Interactive Fuzzy Path Selector.
        Logic ported from widgets.py but encapsulated here.
        """
        current_path = Path(default).resolve() if default else Path.cwd()
        if not current_path.exists():
            current_path = Path.cwd()

        while True:
            try:
                # Get Dirs
                dirs = [
                    d.name
                    for d in current_path.iterdir()
                    if d.is_dir() and not d.name.startswith(".")
                ]
                dirs.sort()
            except PermissionError:
                current_path = current_path.parent
                continue

            choices = [
                Choice(value=".", name=f"✅ SELECT CURRENT: {current_path.name}/"),
                Choice(value="..", name="🔙 .. (Go Up)"),
            ] + [Choice(value=d, name=f"📂 {d}") for d in dirs]

            display_path = str(current_path)
            if len(display_path) > 50:
                display_path = "..." + display_path[-47:]

            try:
                selection = inquirer.fuzzy(
                    message=f"{message} (In: {display_path})",
                    choices=choices,
                    style=self._theme.get_style(),
                    qmark="🔍",
                    pointer="❯",
                    border=False,
                    instruction="(Type to filter, Enter to select)",
                ).execute()
            except KeyboardInterrupt:
                return None

            if selection == ".":
                return current_path
            if selection == "..":
                current_path = current_path.parent
            else:
                current_path = current_path / selection

    # --- UTILS ---

    @contextmanager
    def spinner(
        self, msg: str = "Processing...", spinner_type: str = "dots"
    ) -> Generator[None, None, None]:
        """
        Context manager for safe execution with a spinner.
        Catches exceptions and renders a pretty error panel.
        """
        try:
            with self._console.status(f"[bold blue]{msg}[/]", spinner=spinner_type):
                yield
        except typer.Exit:
            raise
        except Exception as e:
            self.error("Operation Failed", str(e))
            raise typer.Exit(1) from e

    @contextmanager
    def error_boundary(self) -> Generator[None, None, None]:
        """
        Error middleware: wraps CLI flow execution with centralized error handling.

        Catches all exceptions and renders a formatted error panel.
        KeyboardInterrupt is shown as a soft cancellation.
        BaseDddError subclasses are shown with structured context.
        All errors are also printed to stderr for diagnostics.

        Usage:
            with tui.error_boundary():
                run_some_flow(facade)
        """
        try:
            yield
        except KeyboardInterrupt:
            self._console.print("\n[yellow]Action cancelled.[/]")
        except BaseDddError as e:
            self._console.print()
            self.error(
                f"{e.layer_title} Error",
                {
                    "Context": e.context_name,
                    "Message": e.message,
                    "Cause": str(e.original_error) if e.original_error else "—",
                },
            )
            traceback.print_exc(file=sys.stderr)
            self._console.print()
            self.pause()
        except Exception:
            self._console.print("\n[bold red]Unexpected Error:[/bold red]")
            self._console.print_exception(show_locals=False)
            traceback.print_exc(file=sys.stderr)
            self._console.print()
            self.pause()

    def clear(self):
        """Clear the terminal including scrollback buffer."""
        # \033[2J  — clear visible screen
        # \033[3J  — clear scrollback buffer
        # \033[H   — move cursor to top-left
        print("\033[2J\033[3J\033[H", end="", flush=True)

    def pause(self, msg: str = "[dim]Press Enter...[/]"):
        self._console.input(msg)


# Singleton Instance
tui = Tui()
