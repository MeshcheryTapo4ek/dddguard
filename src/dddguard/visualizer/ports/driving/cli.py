import typer
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.align import Align

from dddguard.shared.ports.driving.ui import (
    ask_path,
    print_no_config_warning,
    VISUALIZER_THEME,
    safe_execution
)

from .visualizer_wizard import VisualizerSettingsWizard
from ...adapters.driving import VisualizerController


console = Console()


def register_commands(app: typer.Typer, controller: VisualizerController, config):

    @app.command(name="drawdir")
    def drawdir():
        """🎨 Interactive directory visualizer."""
        run_viz_directory_flow(controller, config)

    @app.command(name="draw")
    def draw():
        """🎨 Visualize project architecture."""
        run_viz_project_flow(controller, config)


# --- PUBLIC FLOWS ---

def run_viz_directory_flow(controller: VisualizerController, config):
    target = ask_path(
        message="Select directory to visualize",
        default=".",
        must_exist=True,
        theme=VISUALIZER_THEME
    )
    if not target:
        return
        
    _run_viz_logic(controller, target, config)


def run_viz_project_flow(controller: VisualizerController, config):
    if not config.project.has_config_file:
        print_no_config_warning()
        target = config.project.absolute_source_path
    else:
        target = config.project.absolute_source_path
        
    _run_viz_logic(controller, target, config)


def _run_viz_logic(controller: VisualizerController, path: Path, config):
    """
    Executes the visualization workflow and renders a styled report.
    """
    wizard = VisualizerSettingsWizard(config)
    
    if not wizard.run():
        return
    
    output_path = Path(wizard.output_file)
    
    # 1. Execution with Spinner
    with safe_execution(status_msg="Generating Diagram...", spinner="earth"):
            controller.draw_architecture(path, output_path)

    # 2. Render Beautiful Success Panel
    _render_success_report(path, output_path)


def _render_success_report(source_path: Path, output_path: Path):
    """
    Private UI helper to render the success panel for Visualizer.
    Uses Purple theme.
    """
    # Grid for aligning labels and values
    grid = Table.grid(padding=(0, 2))
    grid.add_column(style="dim", justify="right")
    grid.add_column(style="bold white")
    
    # Paths info
    # Shorten source path for display if it's too long or use name
    grid.add_row("Source:", str(source_path))
    grid.add_row("Diagram:", f"[purple]{output_path}[/]")
    
    # Spacer
    grid.add_row("", "")
    
    # Viewer Instruction with Clickable Link
    grid.add_row("Viewer:", "[link=https://app.diagrams.net/]https://app.diagrams.net/[/]")
    grid.add_row("", "[dim italic](File -> Open From -> Device)[/]")

    # Create Panel
    panel = Panel(
        Align.center(grid),
        title="[bold purple]🎨 Architecture Map Generated[/]",
        border_style="purple",
        box=box.ROUNDED,
        padding=(1, 2),
        expand=False
    )
    
    console.print()
    console.print(panel)
    console.print()