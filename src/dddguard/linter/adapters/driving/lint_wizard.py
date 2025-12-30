from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator

from dddguard.shared import ConfigVo
from dddguard.shared.adapters.driving import (
    LINTER_THEME,
    ask_select,
)

console = Console()


class LintSettingsWizard:
    """
    Interactive UI Adapter for the Linter.
    Allows the user to view rules or start the analysis.
    """

    def __init__(self, config: ConfigVo):
        self.config = config

    def run(self) -> bool | str:
        """
        Main menu loop.
        Returns:
            True: Run Lint
            False: Cancel/Exit
            str: "view_summary" or "view_matrix"
        """
        console.clear()
        self._render_dashboard()

        choices = [
            Choice(value=True, name="🚀 Run Linter Analysis"),
            Separator(),
            Choice(value="view_summary", name="📖 View Rules Summary"),
            Choice(value="view_matrix", name="🔢 View Rules Matrix"),
            Separator(),
            Choice(value=False, name="❌ Exit"),
        ]

        action = ask_select(
            message=None,
            choices=choices,
            theme=LINTER_THEME,
            instruction="(Use arrow keys to navigate)",
            default=True,
        )

        return action

    def _render_dashboard(self):
        """Renders the context header."""
        color = LINTER_THEME.primary_color

        # Determine display path
        try:
            source_path = self.config.project.absolute_source_path
            path_str = f"./{source_path.relative_to(self.config.project.project_root)}"
        except ValueError:
            path_str = str(self.config.project.absolute_source_path)

        panel = Panel(
            Align.center(f"Target: [bold white]{path_str}[/]"),
            title=f"[bold {color}]Linter Configuration[/]",
            subtitle="[dim]Validate Architecture Rules[/]",
            border_style=color,
            padding=(1, 2),
            expand=True,
        )
        console.print(panel)
