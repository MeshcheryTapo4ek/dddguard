from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator

from dddguard.shared.adapters.driving import (
    LINTER_THEME,
    tui,  # Unified TUI
)
from dddguard.shared.domain import ConfigVo


class LintSettingsWizard:
    """
    Interactive UI Adapter for the Linter.
    """

    def __init__(self, config: ConfigVo) -> None:
        self.config: ConfigVo = config

    def run(self) -> bool | str:
        tui.set_theme(LINTER_THEME)
        tui.clear()
        self._render_dashboard()

        choices = [
            Choice(value=True, name="Run Linter Analysis"),
            Separator(),
            Choice(value="view_summary", name="View Rules Reference (all 13 rules)"),
            Choice(value="view_matrix", name="View Access Matrix (computed from policy)"),
            Separator(),
            Choice(value=False, name="Exit"),
        ]

        action: bool | str = tui.select(
            message=None,
            choices=choices,
            instruction="(Use arrow keys to navigate)",
            default=True,
        )

        return action

    def _render_dashboard(self) -> None:
        try:
            source_path = self.config.project.absolute_source_path
            project_root = self.config.project.project_root
            if source_path and project_root:
                path_str = f"./{source_path.relative_to(project_root)}"
            else:
                path_str = str(source_path) if source_path else "N/A"
        except ValueError:
            path_str = str(self.config.project.absolute_source_path)

        tui.dashboard(
            title="Linter Configuration",
            subtitle="Validate Architecture Rules",
            theme=LINTER_THEME,
            data={"Target": f"[bold white]{path_str}[/]"},
        )
