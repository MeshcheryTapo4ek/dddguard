from rich import box
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from dddguard.shared.adapters.driving import (
    LINTER_THEME,
    tui,  # Unified TUI
)
from dddguard.shared.domain import DirectionEnum, LayerEnum

from ...ports.driving import RulesMatrixSchema


def _format_layer_key(layer: LayerEnum, direction: DirectionEnum) -> str:
    """Formats a (Layer, Direction) pair as a human-readable label."""
    if direction == DirectionEnum.NONE:
        return layer.value
    return f"{layer.value}/{direction.value}"


def _format_key_set(
    keys: frozenset[tuple[LayerEnum, DirectionEnum]],
    style: str = "green",
) -> str:
    """Formats a frozenset of (Layer, Direction) pairs as a styled string."""
    if not keys:
        return "[dim]-[/]"

    items: list[str] = []
    for layer, direction in sorted(keys, key=lambda x: (x[0].value, x[1].value)):
        label = _format_layer_key(layer, direction)
        items.append(f"[{style}]{label}[/]")

    return ", ".join(items)


class RulesViewer:
    """
    Renders all 13 architectural rules in a human-readable format.
    Organized into 4 groups: Internal, Fractal, Cross-Context, Scope Isolation.
    """

    def __init__(self, rules_matrix: RulesMatrixSchema) -> None:
        self.internal_matrix = rules_matrix.internal
        self.fractal = rules_matrix.fractal
        self.outbound_allowed = rules_matrix.outbound_allowed
        self.inbound_allowed = rules_matrix.inbound_allowed
        self.theme_color: str = LINTER_THEME.primary_color

    def render(self) -> None:
        tui.clear()
        self._render_header()

        # Group 1: Internal Layer Access (Rules 1-7)
        self._render_internal_matrix()

        # Group 2: Fractal Rules (Rules 8-9)
        self._render_fractal_rules()

        # Group 3: Cross-Context Rules (Rules 10-11)
        self._render_cross_context_rules()

        # Group 4: Scope Isolation (Rules 12-13)
        self._render_scope_isolation()

        # Bypass Conditions
        self._render_bypass_conditions()

        tui.console.print()
        tui.pause(msg="[dim]Press [bold white]Enter[/] to return to menu...[/]")

    def _render_header(self) -> None:
        tui.console.print(
            Panel(
                "[bold white]DDDGuard — 13 Architectural Dependency Rules[/]",
                subtitle="[italic]Complete Access Matrix[/]",
                border_style=self.theme_color,
                box=box.HEAVY_HEAD,
                expand=True,
            )
        )

    # ==========================================================================
    # GROUP 1: Internal Rules (Same Context)
    # ==========================================================================

    def _render_internal_matrix(self) -> None:
        """Renders the Layer-to-Layer access table (Rules 1-7)."""
        table = Table(
            title="[bold]GROUP 1 — Internal Rules (Same Context)[/]",
            caption="[dim]Rules 1-7: Layer-to-layer dependencies within a single bounded context[/]",
            box=box.ROUNDED,
            expand=True,
            header_style=f"bold {self.theme_color}",
            border_style="dim white",
        )

        table.add_column("Source Layer", style="bold white", width=25)
        table.add_column("Allowed Targets", style="green")
        table.add_column("Forbidden Targets", style="dim red")

        layers_order: list[tuple[LayerEnum, DirectionEnum, str]] = [
            (LayerEnum.DOMAIN, DirectionEnum.NONE, "Domain"),
            (LayerEnum.APP, DirectionEnum.NONE, "App"),
            (LayerEnum.PORTS, DirectionEnum.DRIVING, "Ports / Driving"),
            (LayerEnum.PORTS, DirectionEnum.DRIVEN, "Ports / Driven"),
            (LayerEnum.ADAPTERS, DirectionEnum.DRIVING, "Adapters / Driving"),
            (LayerEnum.ADAPTERS, DirectionEnum.DRIVEN, "Adapters / Driven"),
            (LayerEnum.COMPOSITION, DirectionEnum.NONE, "Composition"),
        ]

        for layer, direction, display_name in layers_order:
            key = (layer, direction)
            if key not in self.internal_matrix:
                continue

            rule = self.internal_matrix[key]
            allowed_str = _format_key_set(rule["allowed"], style="green")
            forbidden_str = _format_key_set(rule["forbidden"], style="dim red")

            table.add_row(display_name.upper(), allowed_str, forbidden_str)

        tui.console.print(table)
        tui.console.print()

    # ==========================================================================
    # GROUP 2: Fractal Rules (Parent <-> Child)
    # ==========================================================================

    def _render_fractal_rules(self) -> None:
        """Renders fractal (parent <-> child) access rules (Rules 8-9)."""
        table = Table(
            title="[bold]GROUP 2 — Fractal Rules (Parent ↔ Child)[/]",
            caption="[dim]Rules 8-9: Nested context boundaries[/]",
            box=box.ROUNDED,
            expand=True,
            header_style="bold yellow",
            border_style="dim yellow",
        )

        table.add_column("Direction", style="bold white", width=25)
        table.add_column("Allowed Targets", style="green")
        table.add_column("Forbidden Targets", style="dim red")

        table.add_row(
            "Child → Parent\n[dim](Upstream)[/]",
            _format_key_set(self.fractal.upstream_allowed, style="green"),
            _format_key_set(self.fractal.upstream_forbidden, style="dim red"),
        )

        table.add_row(
            "Parent → Child\n[dim](Downstream)[/]",
            _format_key_set(self.fractal.downstream_allowed, style="green"),
            _format_key_set(self.fractal.downstream_forbidden, style="dim red"),
        )

        tui.console.print(table)
        tui.console.print()

    # ==========================================================================
    # GROUP 3: Cross-Context Rules (Alien Contexts)
    # ==========================================================================

    def _render_cross_context_rules(self) -> None:
        """Renders cross-context policies (Rules 10-11)."""
        grid = Table.grid(expand=True, padding=(0, 2))
        grid.add_column(ratio=1)
        grid.add_column(ratio=1)

        inbound_list = _format_key_set(self.inbound_allowed, style="green")
        p1 = Panel(
            f"[bold]Accessible layers:[/]\n{inbound_list}\n\n"
            "[dim]Only public driving ports (facades)\nare visible to other contexts.[/]",
            title="[bold green]Rule 11: Inbound (Public API)[/]",
            border_style="green",
            height=9,
        )

        outbound_list = _format_key_set(self.outbound_allowed, style="yellow")
        p2 = Panel(
            f"[bold]Allowed callers:[/]\n{outbound_list}\n\n"
            "[dim]Only driven ports (ACL) may initiate\ncalls to other bounded contexts.[/]",
            title="[bold orange1]Rule 10: Outbound (ACL Only)[/]",
            border_style="orange1",
            height=9,
        )

        grid.add_row(p1, p2)

        tui.console.print(
            Panel(
                grid,
                title="[bold]GROUP 3 — Cross-Context Rules (Alien Contexts)[/]",
                subtitle="[dim]Rules 10-11: ACL-only communication[/]",
                border_style="orange1",
                box=box.ROUNDED,
            )
        )
        tui.console.print()

    # ==========================================================================
    # GROUP 4: Scope Isolation
    # ==========================================================================

    def _render_scope_isolation(self) -> None:
        """Renders scope isolation rules (Rules 12-13)."""
        table = Table(
            title="[bold]GROUP 4 — Scope Isolation[/]",
            caption="[dim]Rules 12-13: Shared & Root boundaries[/]",
            box=box.ROUNDED,
            expand=True,
            header_style="bold cyan",
            border_style="dim cyan",
        )

        table.add_column("Scope", style="bold white", width=25)
        table.add_column("Policy")

        table.add_row(
            "SHARED",
            "[green]Allowed:[/] Shared, Global only\n"
            "[dim red]Forbidden:[/] Context modules, Root\n"
            "[dim]Base of the pyramid — no upward dependencies[/]",
        )

        table.add_row(
            "ROOT",
            "[green]Allowed:[/] Context providers (provider.py), Shared\n"
            "[dim red]Forbidden:[/] Context internals (domain, app, ports, adapters)\n"
            "[dim]Outermost shell — wires providers only[/]",
        )

        tui.console.print(table)
        tui.console.print()

    # ==========================================================================
    # BYPASS CONDITIONS
    # ==========================================================================

    def _render_bypass_conditions(self) -> None:
        """Renders bypass conditions that skip all rule checks."""
        text = Text()
        text.append("These imports are always allowed and skip all rule checks:\n\n", style="dim")
        text.append("  • Target is ", style="white")
        text.append("SHARED", style="bold cyan")
        text.append("  — Shared kernel is globally accessible\n", style="dim")
        text.append("  • Source is ", style="white")
        text.append("COMPOSITION", style="bold cyan")
        text.append(" or ", style="white")
        text.append("GLOBAL", style="bold cyan")
        text.append("  — Wiring layers can import freely\n", style="dim")
        text.append("  • Missing ", style="white")
        text.append("ComponentPassport", style="bold cyan")
        text.append("  — Unclassified nodes cannot be validated\n", style="dim")

        tui.console.print(
            Panel(
                text,
                title="[bold]BYPASS CONDITIONS[/]",
                border_style="dim green",
                box=box.ROUNDED,
            )
        )
