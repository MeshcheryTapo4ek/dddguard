from pathlib import Path
from typing import Optional, Union
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.text import Text

from .themes import GuardTheme, DEFAULT_THEME

console = Console()


def render_config_info(config, theme: GuardTheme = DEFAULT_THEME):
    """
    Renders detailed configuration info: Source, Tests, Docs, Macros.
    """
    color = theme.primary_color

    # Grid for path details
    grid = Table.grid(padding=(0, 2))
    grid.add_column(style="dim", justify="right", min_width=15)
    grid.add_column(style="bold white")

    root = config.project.project_root

    def fmt_path(p: Union[Path, str]) -> str:
        # 1. Ensure we have a Path object
        path_obj = Path(p)

        # 2. If it's already relative, just decorate it
        if not path_obj.is_absolute():
            return f"./{path_obj}"

        # 3. If absolute, try to show relative to root
        try:
            rel = path_obj.relative_to(root)
            return f"./{rel}"
        except ValueError:
            # Not within root, return full path
            return str(path_obj)

    grid.add_row("📍 Project Root:", str(root.name))

    # Safe rendering of potentially missing fields or strings
    src = getattr(config.project, "source_dir", "src")
    grid.add_row("📂 Source Code:", f"[{color}]{fmt_path(src)}[/]")

    # Optional fields (if your ConfigVo has them)
    if hasattr(config.project, "tests_dir"):
        grid.add_row("🧪 Tests:", fmt_path(config.project.tests_dir))

    if hasattr(config.project, "docs_dir"):
        grid.add_row("📚 Docs:", fmt_path(config.project.docs_dir))
    
    # --- MACRO CONTEXTS DISPLAY ---
    macros = config.project.macro_contexts
    if macros:
        # Spacer
        grid.add_row("", "") 
        first = True
        for zone, folder in macros.items():
            label = "🌐 Macro Zones:" if first else ""
            # Format: "scanner -> src/scanner"
            grid.add_row(label, f"[cyan bold]{zone.upper()}[/] ➜ [dim]{folder}[/]")
            first = False

    console.print(
        Panel(
            Align.center(grid),
            title=f"[bold {color}]Current Configuration[/]",
            border_style=color,
            padding=(1, 2),
            expand=False,
        )
    )


def render_dashboard(
    config,
    config_path: Optional[Path],
    theme: GuardTheme = DEFAULT_THEME,
    show_context: bool = True,
):
    """
    Main dashboard renderer.
    """
    color = theme.primary_color
    title = Text("DDDGuard Architecture Suite", style="bold white")

    content = Table.grid(expand=True)
    content.add_column(justify="center")
    content.add_row(title)

    # Only show context line if requested
    if show_context:
        subtitle = Text(f"Context: {theme.name.upper()}", style=f"italic {color}")
        content.add_row(subtitle)

    content.add_row("")

    if config_path:
        # Config exists
        content.add_row(Text("✅ Configuration Loaded", style="bold green"))
        content.add_row("")

        # Grid for path details
        grid = Table.grid(padding=(0, 2))
        grid.add_column(style="dim", justify="right")
        grid.add_column(style="bold white")

        root = config.project.project_root

        # Robust path formatting logic duplicated/inlined for autonomy
        src_raw = getattr(config.project, "source_dir", "src")
        src_path = Path(src_raw)

        if src_path.is_absolute():
            try:
                src_str = f"./{src_path.relative_to(root)}"
            except ValueError:
                src_str = str(src_path)
        else:
            src_str = f"./{src_path}"

        grid.add_row("Project:", root.name)
        grid.add_row("Source:", f"[{color}]{src_str}[/]")
        grid.add_row("Config:", f"[dim]{config_path.name}[/]")

        # Quick Macro summary in Dashboard
        macro_count = len(config.project.macro_contexts)
        if macro_count > 0:
             grid.add_row("Macros:", f"[{color}]{macro_count} defined[/]")

        content.add_row(Align.center(grid))

    else:
        # No Config
        content.add_row(Text("⚠️  Running in Ad-Hoc Mode", style="bold yellow"))
        content.add_row(Text("No config.yaml found in project.", style="dim"))

    console.print(Panel(content, border_style=color, padding=(1, 2), expand=True))


def print_no_config_warning():
    """
    Standard warning when config is missing for a command that prefers it.
    """
    console.print()
    console.print(
        Panel(
            "[bold yellow]⚠️  Configuration Missing[/bold yellow]\n\n"
            "This command works best with a [cyan]config.yaml[/cyan].\n"
            "We are using default settings.\n\n"
            "👉 Run [bold green]dddguard init[/bold green] or [bold green]dddguard config[/bold green] to set up.",
            border_style="yellow",
            expand=False,
        )
    )
    console.print()