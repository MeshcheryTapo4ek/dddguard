from typing import Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from dddguard.shared import ContextLayerEnum
from dddguard.shared.ports.driving.ui import LINTER_THEME


console = Console()


class RulesViewer:
    """
    Renders the architectural rules matrix in a human-readable format.
    """
    def __init__(self, rules_data: Dict[str, Any]):
        self.internal_matrix = rules_data.get("internal", {})
        self.public_layers = rules_data.get("public", set())
        self.outbound_layers = rules_data.get("outbound", set())
        self.theme_color = LINTER_THEME.primary_color

    def render(self):
        console.clear()
        self._render_header()
        
        # 1. Internal Layer Access (The Matrix)
        self._render_internal_matrix()
        
        # 2. Cross-Context Rules (Public/Outbound)
        self._render_cross_context_rules()
        
        console.print()
        console.print(Panel(
            "[dim]Press [bold white]Enter[/] to return to menu...[/]",
            style=f"dim {self.theme_color}",
            box=box.SIMPLE
        ))
        console.input()

    def _render_header(self):
        console.print(Panel(
            "[bold white]Architectural Rules & Constraints[/]",
            subtitle="[italic]Domain-Driven Design Guidelines[/]",
            border_style=self.theme_color,
            box=box.HEAVY_HEAD,
            expand=True
        ))

    def _render_internal_matrix(self):
        """Renders the Layer-to-Layer access table."""
        table = Table(
            title="🛑 Internal Layer Boundaries (Intra-Context)",
            title_style="bold white",
            box=box.ROUNDED,
            expand=True,
            header_style=f"bold {self.theme_color}",
            border_style="dim white"
        )

        table.add_column("Source Layer", style="bold white", width=20)
        table.add_column("Can Import (Allowed)", style="green")
        table.add_column("Cannot Import (Forbidden)", style="dim red")

        # Sort layers logically
        layers_order = [
            ContextLayerEnum.DOMAIN,
            ContextLayerEnum.APP,
            ContextLayerEnum.DRIVING_ADAPTERS,
            ContextLayerEnum.DRIVEN_ADAPTERS,
            ContextLayerEnum.COMPOSITION
        ]

        for layer in layers_order:
            if layer not in self.internal_matrix:
                continue
                
            rule = self.internal_matrix[layer]
            
            # Format Allowed
            allowed = rule.get("allowed", set())
            if not allowed:
                allowed_str = "[dim]-[/]"
            else:
                # Highlight logic: Domain is special
                items = []
                for l in allowed:
                    if l == ContextLayerEnum.DOMAIN:
                        items.append(f"[bold underline]{l.value}[/]")
                    else:
                        items.append(l.value)
                allowed_str = ", ".join(items)

            # Format Forbidden
            forbidden = rule.get("forbidden", set())
            if not forbidden:
                forbidden_str = "[dim]None[/]"
            else:
                forbidden_str = ", ".join([l.value for l in forbidden])

            table.add_row(
                layer.value.upper(),
                allowed_str,
                forbidden_str
            )

        console.print(table)

    def _render_cross_context_rules(self):
        """Renders policies for interaction between Bounded Contexts."""
        
        # Grid to hold two panels side-by-side
        grid = Table.grid(expand=True, padding=(0, 2))
        grid.add_column(ratio=1)
        grid.add_column(ratio=1)

        # Panel 1: Public Interface
        public_list = "\n".join([f"• [cyan]{l.value}[/]" for l in self.public_layers])
        p1 = Panel(
            public_list,
            title="[bold green]🔓 Public Layers[/]",
            subtitle="(Accessible from other Contexts)",
            border_style="green",
            height=8
        )

        # Panel 2: Outbound Initiators
        outbound_list = "\n".join([f"• [yellow]{l.value}[/]" for l in self.outbound_layers])
        p2 = Panel(
            outbound_list,
            title="[bold orange1]📡 Outbound Initiators[/]",
            subtitle="(Can call other Contexts)",
            border_style="orange1",
            height=8
        )

        grid.add_row(p1, p2)
        
        console.print()
        console.print("[bold white]🌐 Cross-Context Policies[/]")
        console.print(grid)