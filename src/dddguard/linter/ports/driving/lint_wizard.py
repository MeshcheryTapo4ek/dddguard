from typing import List, Any
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich import box

from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator

from dddguard.shared.ports.driving.ui import (
    LINTER_THEME, 
    ask_select, 
)

console = Console()

class LintSettingsWizard:
    """
    Launcher for the Linter with options to view rules.
    """
    def __init__(self, config):
        self.config = config
        self.settings = {
            "verbose": False, 
            "strict": True,
        }

    def run(self) -> Any:
        """
        Returns:
            - True: Run Scan
            - False: Cancel
            - "SHOW_SUMMARY": View High-level rules
            - "SHOW_MATRIX": View Detailed Matrix
        """
        last_pointer_value = "run"

        while True:
            console.clear()
            self._render_dashboard()
            
            choices = self._build_menu()
            
            action = ask_select(
                message=None,
                choices=choices,
                default=last_pointer_value,
                theme=LINTER_THEME,
                instruction=""
            )
            
            if action is None or action == "cancel":
                return False
            
            if action == "run":
                return True
            
            # Return special signals to the CLI controller
            if action in ["view_summary", "view_matrix"]:
                return action
            
            last_pointer_value = action

    def _render_dashboard(self):
        primary = LINTER_THEME.primary_color
        
        # --- Header (Project Info) ---
        project_name = self.config.project.project_root.name
        src_path = self.config.project.source_dir
        
        header_text = Text()
        header_text.append(f"Linting Target: ", style="dim")
        header_text.append(f"{project_name}/{src_path}", style=f"bold {primary}")
        
        panel = Panel(
            Align.center(header_text),
            title=f"[bold {primary}] ARCHITECTURE GUARD [/]",
            subtitle="[dim]Arrows to Navigate • Enter to Select[/]",
            subtitle_align="right",
            border_style=primary,
            padding=(1, 2),
            box=box.ROUNDED,
            expand=True
        )
        console.print(panel)

    def _build_menu(self) -> List[Any]:
        return [
            Separator(" REFERENCE "),
            Choice(value="view_summary", name="   📖 View Rules (Summary)"),
            Choice(value="view_matrix", name="   🔢 View Rules (Matrix)"),
            
            Separator(),
            Choice(value="run", name=">>> RUN VALIDATION <<<"),
            Choice(value="cancel", name="   Exit / Cancel")
        ]