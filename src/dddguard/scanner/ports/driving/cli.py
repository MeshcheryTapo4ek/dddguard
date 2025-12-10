import typer
import json

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.align import Align

# --- UI IMPORTS ---
from dddguard.shared.ports.driving.ui import (
    render_config_info,
    SCANNER_THEME, 
    ask_path,
    print_no_config_warning,
    safe_execution
)

# --- INFRASTRUCTURE IMPORTS ---
from dddguard.shared.adapters.driven import YamlConfigLoader

# --- ADAPTER IMPORTS ---
from ...adapters.driving import ScannerController

# --- WIZARD ---
from .scan_options import ScanOptions
from .scan_wizard import ScanSettingsWizard

console = Console()

def register_commands(app: typer.Typer, controller: ScannerController):
    
    @app.command(name="scandir")
    def scandir():
        """Interactive directory scanner."""
        run_scan_directory_flow(controller)

    @app.command(name="scan")
    def scan():
        """Project scanner (uses config)."""
        run_scan_project_flow(controller)


# --- PUBLIC FLOWS ---

def run_scan_directory_flow(controller: ScannerController):
    target_path = ask_path(
        message="Select directory to scan",
        default=".",
        must_exist=True,
        theme=SCANNER_THEME
    )
    
    if not target_path:
        return 

    options = ScanOptions(target_path=target_path)
    wizard = ScanSettingsWizard(options, controller.config)
    if wizard.run():
        _execute_scan(controller, options)


def run_scan_project_flow(controller: ScannerController):
    loader = YamlConfigLoader()
    config_path = loader._discover_config_file()
    
    if config_path is None:
        print_no_config_warning()
        run_scan_directory_flow(controller)
        return

    render_config_info(controller.config, theme=SCANNER_THEME)
    
    options = ScanOptions(
        target_path=controller.config.project.absolute_source_path,
        scan_all=False, 
        show_root=True,
        show_shared=True
    )

    wizard = ScanSettingsWizard(options, controller.config)
    if wizard.run():
        _execute_scan(controller, options)


def _execute_scan(controller: ScannerController, opts: ScanOptions):
    """
    Internal execution logic.
    Refactored to show a beautiful success report using DTO data.
    """
    mode_msg = "ALL files" if opts.scan_all else "Python files"
    
    # 1. Spinner while working
    with safe_execution(status_msg=f"Scanning... ({mode_msg})"):
        # Call Adapter -> Returns DTO
        dto = controller.scan_directory(
            path=opts.target_path, 
            whitelist_contexts=opts.contexts, 
            whitelist_layers=opts.layers,
            show_root=opts.show_root,
            show_shared=opts.show_shared,
            dirs_only=opts.dirs_only, 
            scan_all=opts.scan_all
        )
        
        # Save JSON
        with open(opts.output_json, "w", encoding="utf-8") as f:
            json.dump(dto.source_tree, f, indent=2, ensure_ascii=False)

    # 2. Render Beautiful Success Panel
    _render_success_report(dto, opts.output_json)


def _render_success_report(dto, output_file):
    """
    Private UI helper to render the results panel.
    """
    # Grid for aligning labels and values
    grid = Table.grid(padding=(0, 2))
    grid.add_column(style="dim", justify="right")  # Labels
    grid.add_column(style="bold white")            # Values
    
    # Add Metrics
    grid.add_row("Contexts Found:", f"[cyan]{dto.context_count}[/]")
    grid.add_row("Files Processed:", f"[cyan]{dto.file_count}[/]")
    
    # Separator row (empty)
    grid.add_row("", "")
    
    # Add Output Info
    grid.add_row("Output File:", f"[green]{output_file}[/]")

    # Create Panel
    panel = Panel(
        Align.center(grid),
        title="[bold green]✅ Scan Completed Successfully[/]",
        border_style="green",
        box=box.ROUNDED,
        padding=(1, 2),
        expand=False
    )
    
    console.print()
    console.print(panel)
    console.print()