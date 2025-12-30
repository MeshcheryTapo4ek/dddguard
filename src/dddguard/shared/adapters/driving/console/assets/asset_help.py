from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.box import ROUNDED, SIMPLE


def get_linter_help_renderable():
    """
    Returns a Rich Renderable object describing the Linter Rules.
    Used for CLI help and interactive rule viewing.
    """

    # Grid for Layout
    grid = Table.grid(expand=True, padding=(0, 2))
    grid.add_column(ratio=1)

    # 1. Header
    grid.add_row(
        Text("🚀 Validates Architecture Rules on the main project.", style="bold cyan")
    )
    grid.add_row(
        Text(
            "The Linter enforces strict DDD constraints based on the Laws of Clean Architecture.",
            style="italic dim",
        )
    )
    grid.add_row("")

    # 2. Layer Rules Table
    table = Table(box=SIMPLE, show_header=True, header_style="bold white", expand=True)
    table.add_column("Layer", style="bold", width=20)
    table.add_column("Rules & Restrictions")

    table.add_row(
        "[blue]🔵 DOMAIN[/]",
        "• Must be [bold green]PURE[/].\n• Can ONLY import [cyan]SHARED KERNEL[/] and itself.",
    )
    table.add_row(
        "[magenta]🟣 APP[/]",
        "• Imports [blue]DOMAIN[/] & [cyan]SHARED[/].\n• ⛔ NO DTOs (Pure Domain Language).\n• ⛔ NO INFRASTRUCTURE (Adapters/Ports).",
    )
    table.add_row(
        "[green]🔌 ADAPTERS[/]",
        "[bold green]🟢 DRIVING (Controllers):[/]\n  • Calls [magenta]APP[/] UseCases.\n  • ⛔ NO PORTS (No DB/Config).\n\n[bold orange1]🟠 DRIVEN (Repositories/ACL):[/]\n  • Implements [magenta]APP[/] Interfaces.\n  • ✅ USES [dim]DRIVEN PORTS[/] (DB Sessions).\n  • ✅ CROSS-CONTEXT (Calls other contexts).",
    )
    table.add_row(
        "[white]📄 DTOs[/]",
        "• Dumb Data Contracts.\n• ⛔ NO LOGIC DEPS (No App/Adapters).",
    )
    table.add_row(
        "[dim]⚙️ PORTS[/]",
        "[bold green]🟢 DRIVING (Frameworks):[/] Imports Driving Adapters.\n[bold orange1]🟠 DRIVEN (Drivers):[/] Low-level tools. Isolated.",
    )

    grid.add_row(
        Panel(table, title="🧱 LAYER ISOLATION RULES", border_style="blue", box=ROUNDED)
    )
    grid.add_row("")

    # 3. Cross Context
    cross_text = Text()
    cross_text.append("🚧 CROSS-CONTEXT BOUNDARIES:\n", style="bold yellow")
    cross_text.append(" • Source: Only ", style="white")
    cross_text.append("DRIVEN ADAPTERS (ACL)", style="bold orange1")
    cross_text.append(" can initiate calls.\n", style="white")
    cross_text.append(" • Target: Can only import ", style="white")
    cross_text.append("DRIVING ADAPTERS (Facades)", style="bold green")
    cross_text.append(" or ", style="white")
    cross_text.append("DRIVING DTOs", style="bold white")
    cross_text.append(".", style="white")

    grid.add_row(Panel(cross_text, border_style="yellow", box=ROUNDED))

    return grid
