from pathlib import Path

import typer

from dddguard.shared.adapters.driving import (
    VISUALIZER_THEME,
    tui,  # Unified TUI
)

from ...ports.driving.visualizer_facade import VisualizerFacade
from .visualizer_wizard import VisualizerSettingsWizard


def register_commands(app: typer.Typer, facade: VisualizerFacade, config):
    @app.command(name="drawdir")
    def drawdir():
        """🎨 Interactive directory visualizer."""
        run_viz_directory_flow(facade, config)

    @app.command(name="draw")
    def draw():
        """🎨 Visualize project architecture."""
        run_viz_project_flow(facade, config)


# --- PUBLIC FLOWS ---


def run_viz_directory_flow(facade: VisualizerFacade, config):
    tui.set_theme(VISUALIZER_THEME)
    target = tui.path(message="Select directory to visualize", default=".")
    if not target:
        return

    _run_viz_logic(facade, target, config)


def run_viz_project_flow(facade: VisualizerFacade, config):
    tui.set_theme(VISUALIZER_THEME)
    if config.project.config_file_path is None:
        tui.warning("Configuration Missing", "Using default source root.")
    target = config.project.absolute_source_path

    _run_viz_logic(facade, target, config)


def _run_viz_logic(facade: VisualizerFacade, path: Path, config):
    """
    Executes the visualization workflow and renders a styled report.
    Loops to allow re-configuration after generation.
    """
    # 1. Init Wizard (Stateful - keeps settings between runs)
    wizard = VisualizerSettingsWizard(config)

    while True:
        # 2. Run Wizard to get DTO (Contract) or None (Exit)
        dto = wizard.run()

        if not dto:
            return  # User selected Cancel/Exit

        # 3. Execution with Spinner
        with tui.spinner("Generating Diagram...", spinner_type="earth"):
            # Pass the DTO to the facade (Port)
            facade.draw_architecture(path, dto)

        # 4. Render Beautiful Success Panel
        # We pass the clickable link as a value
        tui.success(
            "Diagram Generated",
            {
                "Source": str(path),
                "Output": f"[purple]{dto.output_file}[/]",
                "Viewer": "[link=https://app.diagrams.net/]diagrams.net[/]",
                "Note": "[dim]Open via File -> Open From -> Device[/]",
            },
        )

        # 5. PAUSE: Wait for user input before looping back to main menu
        tui.pause("[dim]Press Enter to return to menu...[/]")
