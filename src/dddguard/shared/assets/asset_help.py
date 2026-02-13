from rich.box import ROUNDED, SIMPLE
from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .text_content_data import (
    BYPASS_RULES_DATA,
    CROSS_CONTEXT_RULES_TABLE_DATA,
    FRACTAL_RULES_TABLE_DATA,
    INTERNAL_RULES_TABLE_DATA,
    SCOPE_RULES_TABLE_DATA,
)


def _build_rules_table(
    data: list[tuple[str, str]],
    *,
    source_col: str = "Source Layer",
    rules_col: str = "Access Rules",
    header_color: str = "bold white",
) -> Table:
    """Builds a Rich table from structured rule data."""
    table = Table(
        box=SIMPLE,
        show_header=True,
        header_style=header_color,
        expand=True,
    )
    table.add_column(source_col, style="bold", width=22)
    table.add_column(rules_col)

    for label, description in data:
        table.add_row(label, description)

    return table


def get_linter_help_renderable() -> RenderableType:
    """
    Returns a Rich Renderable object describing all 13 Linter Rules.
    Organized into 4 groups + bypass conditions.
    Used for CLI help and interactive rule viewing.
    """

    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(ratio=1)

    # Header
    grid.add_row(
        Text(
            "DDDGuard validates every import against 13 architectural rules.",
            style="bold cyan",
        )
    )
    grid.add_row(
        Text(
            "Rules are organized into 4 groups by context relationship.",
            style="italic dim",
        )
    )
    grid.add_row("")

    # GROUP 1: Internal Rules (Same Context) — Rules 1-7
    internal_table = _build_rules_table(INTERNAL_RULES_TABLE_DATA)
    grid.add_row(
        Panel(
            internal_table,
            title="[bold]GROUP 1 — Internal Rules (Same Context)[/]",
            subtitle="[dim]Rules 1-7: Layer-to-layer dependencies[/]",
            border_style="blue",
            box=ROUNDED,
        )
    )
    grid.add_row("")

    # GROUP 2: Fractal Rules (Parent <-> Child) — Rules 8-9
    fractal_table = _build_rules_table(
        FRACTAL_RULES_TABLE_DATA,
        source_col="Direction",
    )
    grid.add_row(
        Panel(
            fractal_table,
            title="[bold]GROUP 2 — Fractal Rules (Parent ↔ Child)[/]",
            subtitle="[dim]Rules 8-9: Nested context boundaries[/]",
            border_style="yellow",
            box=ROUNDED,
        )
    )
    grid.add_row("")

    # GROUP 3: Cross-Context Rules (Alien Contexts) — Rules 10-11
    cross_table = _build_rules_table(
        CROSS_CONTEXT_RULES_TABLE_DATA,
        source_col="Boundary",
    )
    grid.add_row(
        Panel(
            cross_table,
            title="[bold]GROUP 3 — Cross-Context Rules (Alien Contexts)[/]",
            subtitle="[dim]Rules 10-11: ACL-only communication[/]",
            border_style="orange1",
            box=ROUNDED,
        )
    )
    grid.add_row("")

    # GROUP 4: Scope Isolation — Rules 12-13
    scope_table = _build_rules_table(
        SCOPE_RULES_TABLE_DATA,
        source_col="Scope",
    )
    grid.add_row(
        Panel(
            scope_table,
            title="[bold]GROUP 4 — Scope Isolation[/]",
            subtitle="[dim]Rules 12-13: Shared & Root boundaries[/]",
            border_style="cyan",
            box=ROUNDED,
        )
    )
    grid.add_row("")

    # BYPASS CONDITIONS
    bypass_text = Text()
    bypass_text.append("Imports matching these conditions skip all rule checks:\n\n", style="dim")
    for condition, rationale in BYPASS_RULES_DATA:
        bypass_text.append("  • ", style="white")
        bypass_text.append_text(Text.from_markup(condition))
        bypass_text.append(f"  — {rationale}\n", style="dim")

    grid.add_row(
        Panel(
            bypass_text,
            title="[bold]BYPASS CONDITIONS[/]",
            subtitle="[dim]Always allowed — skip all checks[/]",
            border_style="dim green",
            box=ROUNDED,
        )
    )

    return grid
