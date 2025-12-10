from typing import List, Any
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.table import Table
from rich import box

from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator

from dddguard.shared.ports.driving.ui import (
    VISUALIZER_THEME, 
    ask_select, 
    ask_text
)

console = Console()

class VisualizerSettingsWizard:
    """
    Interactive HUD for configuring the diagram generation.
    """
    def __init__(self, config):
        self.config = config
        self.output_file = "architecture.drawio"
        self.theme_color = VISUALIZER_THEME.primary_color

    def run(self) -> bool:
        """
        Main Loop.
        Returns True to proceed, False to cancel.
        """
        last_pointer = "run"

        while True:
            console.clear()
            self._render_dashboard()
            
            choices = self._build_menu()
            
            action = ask_select(
                message=None, 
                choices=choices, 
                default=last_pointer,
                theme=VISUALIZER_THEME,
                instruction=""
            )
            
            if action is None or action == "cancel":
                return False
            
            if action == "run":
                return True
            
            if action == "edit_output":
                self._edit_output_filename()
            
            last_pointer = action

    def _edit_output_filename(self):
        new_val = ask_text(
            "Enter filename (.drawio)", 
            default=self.output_file, 
            theme=VISUALIZER_THEME
        )
        if new_val:
            if not new_val.endswith(".drawio"):
                new_val += ".drawio"
            self.output_file = new_val

    def _render_dashboard(self):
        color = self.theme_color
        
        # --- Header (Project Info) ---
        project_name = self.config.project.project_root.name
        src_path = self.config.project.source_dir
        
        header_text = Text()
        header_text.append(f"Visualization Target: ", style="dim")
        header_text.append(f"{project_name}/{src_path}", style=f"bold {color}")

        # --- Settings Grid ---
        grid = Table.grid(padding=(0, 2))
        grid.add_column(style="dim", justify="right", min_width=15)
        grid.add_column(style="bold white")
        
        grid.add_row("Format:", "Draw.io XML")
        grid.add_row("Engine:", "NetworkX + Rich")
        grid.add_row("Output File:", f"[{color}]{self.output_file}[/]")

        # --- Main Panel ---
        # Group allows us to stack the Header and the Grid inside one Panel
        content = Group(
            Align.center(header_text),
            Text(" "), # Spacer
            Align.center(grid)
        )

        panel = Panel(
            content,
            title=f"[bold {color}] ARCHITECTURE MAPPER [/]",
            subtitle="[dim]Arrows to Navigate • Enter to Select[/]",
            subtitle_align="right",
            border_style=color,
            padding=(1, 2),
            box=box.ROUNDED,
            expand=True
        )
        console.print(panel)

    def _build_menu(self) -> List[Any]:
        return [
            Separator(" SETTINGS "),
            Choice(value="edit_output", name=f"   💾 Output File ({self.output_file})"),
            
            Separator(),
            Choice(value="run", name=">>> GENERATE DIAGRAM <<<"),
            Choice(value="cancel", name="   Exit / Cancel")
        ]