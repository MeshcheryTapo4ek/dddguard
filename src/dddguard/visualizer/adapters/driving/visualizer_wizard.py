from typing import List, Any
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.table import Table
from rich import box

from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator

from dddguard.shared.adapters.driving import (
    VISUALIZER_THEME,
    ask_select,
    ask_text,
    ask_multiselect
)

from ...ports.driving import DrawOptionsDto

console = Console()


class VisualizerSettingsWizard:
    def __init__(self, config):
        self.config = config
        self.theme_color = VISUALIZER_THEME.primary_color
        
        # State
        self.show_errors = True
        self.hide_root_arrows = True
        self.hide_shared_arrows = True
        self.output_file = "architecture.drawio"

    def run(self) -> DrawOptionsDto | None:
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
                instruction="",
            )

            if action is None or action == "cancel":
                return None

            if action == "run":
                return self._build_dto()

            if action == "edit_output":
                self._edit_output_filename()
            
            elif action == "edit_filters":
                self._edit_filters()

            last_pointer = action

    def _build_dto(self) -> DrawOptionsDto:
        return DrawOptionsDto(
            show_errors=self.show_errors,
            hide_root_arrows=self.hide_root_arrows,
            hide_shared_arrows=self.hide_shared_arrows,
            output_file=self.output_file,
        )

    def _edit_filters(self):
        choices = [
            Choice(value="errors", name="Show Errors/Exceptions", enabled=self.show_errors),
            Separator(),
            Choice(value="hide_root", name="Hide Wiring (Root -> *)", enabled=self.hide_root_arrows),
            Choice(value="hide_shared", name="Hide Common (* -> Shared)", enabled=self.hide_shared_arrows),
        ]
        
        console.clear()
        console.print(Panel("[bold white]Graph Visibility Settings[/]", border_style=self.theme_color))
        
        selected = ask_multiselect(
            message=None,
            choices=choices,
            theme=VISUALIZER_THEME
        )
        
        if selected is not None:
            self.show_errors = "errors" in selected
            self.hide_root_arrows = "hide_root" in selected
            self.hide_shared_arrows = "hide_shared" in selected

    def _edit_output_filename(self):
        new_val = ask_text(
            message="Enter filename (.drawio)",
            default=self.output_file,
            theme=VISUALIZER_THEME,
        )
        if new_val:
            if not new_val.endswith(".drawio"):
                new_val += ".drawio"
            self.output_file = new_val

    def _render_dashboard(self):
        color = self.theme_color
        grid = Table.grid(padding=(0, 2))
        grid.add_column(style="dim", justify="right", min_width=15)
        grid.add_column(style="bold white")

        grid.add_row("Output:", f"[{color}]{self.output_file}[/]")
        grid.add_row("Errors:", "Visible" if self.show_errors else "[dim]Hidden[/]")
        
        # New Status Logic
        root_st = "Hidden (Clean)" if self.hide_root_arrows else "[dim]Show All[/]"
        grid.add_row("Wiring (Root):", root_st)
        
        shared_st = "Hidden (Clean)" if self.hide_shared_arrows else "[dim]Show All[/]"
        grid.add_row("Shared Deps:", shared_st)

        content = Group(Align.center(Text("ARCHITECTURAL MAPPER", style="bold " + color)), Text(" "), Align.center(grid))
        panel = Panel(
            content,
            border_style=color,
            padding=(1, 2),
            box=box.ROUNDED,
            expand=True,
        )
        console.print(panel)

    def _build_menu(self) -> List[Any]:
        return [
            Separator(" CONFIGURATION "),
            Choice(value="edit_filters", name="  🔍 Filters & Noise Reduction..."),
            Choice(value="edit_output", name=f"  💾 Output File ({self.output_file})"),
            Separator(),
            Choice(value="run", name=">>> GENERATE DIAGRAM <<<"),
            Choice(value="cancel", name="  Exit / Cancel"),
        ]