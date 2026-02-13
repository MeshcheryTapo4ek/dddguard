from typing import Any

from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator

from dddguard.shared.adapters.driving import (
    VISUALIZER_THEME,
    tui,  # Unified TUI
)

from ...ports.driving.visualizer_facade import DrawOptionsDto


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
        tui.set_theme(VISUALIZER_THEME)

        while True:
            tui.clear()
            self._render_dashboard()

            choices = self._build_menu()

            action = tui.select(
                message=None,
                choices=choices,
                default=last_pointer,
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
            Choice(
                value="hide_root",
                name="Hide Wiring (Root -> *)",
                enabled=self.hide_root_arrows,
            ),
            Choice(
                value="hide_shared",
                name="Hide Common (* -> Shared)",
                enabled=self.hide_shared_arrows,
            ),
        ]

        tui.clear()
        tui.console.print("[bold white]Graph Visibility Settings[/]")

        selected = tui.multiselect(message=None, choices=choices)

        if selected is not None:
            self.show_errors = "errors" in selected
            self.hide_root_arrows = "hide_root" in selected
            self.hide_shared_arrows = "hide_shared" in selected

    def _edit_output_filename(self):
        new_val = tui.text(
            message="Enter filename (.drawio)",
            default=self.output_file,
        )
        if new_val:
            if not new_val.endswith(".drawio"):
                new_val += ".drawio"
            self.output_file = new_val

    def _render_dashboard(self):
        tui.dashboard(
            title="ARCHITECTURAL MAPPER",
            theme=VISUALIZER_THEME,
            data={
                "Output": f"[{self.theme_color}]{self.output_file}[/]",
                "Errors": "Visible" if self.show_errors else "[dim]Hidden[/]",
                "Wiring (Root)": "Hidden (Clean)" if self.hide_root_arrows else "[dim]Show All[/]",
                "Shared Deps": "Hidden (Clean)" if self.hide_shared_arrows else "[dim]Show All[/]",
            },
        )

    def _build_menu(self) -> list[Any]:
        return [
            Separator(" CONFIGURATION "),
            Choice(value="edit_filters", name="  🔍 Filters & Noise Reduction..."),
            Choice(value="edit_output", name=f"  💾 Output File ({self.output_file})"),
            Separator(),
            Choice(value="run", name=">>> GENERATE DIAGRAM <<<"),
            Choice(value="cancel", name="  Exit / Cancel"),
        ]
