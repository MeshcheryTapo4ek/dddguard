import typer
from pathlib import Path

from rich.console import Console
from rich import box
from rich.table import Table
from rich.panel import Panel
from rich.align import Align

# --- UI IMPORTS ---
from dddguard.shared.ports.driving.ui import (
    ask_path,
    print_no_config_warning,
    LINTER_THEME,
    safe_execution
)
from dddguard.shared.assets import get_linter_help_renderable

# --- ADAPTERS ---
from ...adapters.driving import LinterController
from .lint_wizard import LintSettingsWizard
from .rules_viewer import RulesViewer

console = Console()

def register_commands(app: typer.Typer, controller: LinterController, config):

    @app.command(name="lintdir")
    def lintdir():
        """
        🛡️ Lint a SPECIFIC directory.
        Run with --help to see rules.
        """
        run_lint_directory_flow(controller)

    @app.command(name="lint")
    def lint():
        """
        🛡️ Lint project architecture.
        
        Runs static analysis to ensure Domain-Driven Design rules are respected.
        """
        run_lint_project_flow(controller)


# --- PUBLIC FLOWS ---

def run_lint_directory_flow(controller: LinterController):
    target = ask_path(
        message="Select directory to lint",
        default=".",
        must_exist=True,
        theme=LINTER_THEME
    )
    if not target:
        return
        
    _run_lint_logic(controller, target)


def run_lint_project_flow(controller: LinterController):
    config = controller.config
    if not config.project.has_config_file:
        print_no_config_warning()
        target = config.project.absolute_source_path
    else:
        target = config.project.absolute_source_path

    _run_lint_logic(controller, target)


def _run_lint_logic(controller: LinterController, path: Path):
    """
    Launch Wizard then Execute.
    """
    wizard = LintSettingsWizard(controller.config)
    
    # Wizard Loop
    while True:
        result = wizard.run()
        
        if result is False: 
            return
            
        if result == "view_summary":
            console.clear()
            console.print(get_linter_help_renderable())
            
            console.print("\n[dim]Press [bold white]Enter[/] to return...[/]")
            console.input()
            continue
        
        # 2. VIEW MATRIX (Detailed table)
        if result == "view_matrix":
            rules_data = controller.get_rules_matrix()
            viewer = RulesViewer(rules_data)
            viewer.render() 
            continue
            
        if result is True: # Run
            break
        
    # Execute Scan
    with safe_execution(status_msg="Checking architecture...", spinner="dots"):
        response = controller.lint_project(path)
            
    # Report
    _print_report(response)


def _print_report(response_dto):
    console.print()
    
    if response_dto.success:
        # --- SUCCESS STATE ---
        grid = Table.grid(padding=(0, 2))
        grid.add_column(style="dim", justify="right")
        grid.add_column(style="bold white")
        
        grid.add_row("Files Scanned:", f"{response_dto.total_scanned}")
        grid.add_row("Violations:", "[green]0[/]")
        grid.add_row("Status:", "[bold green]PASSED[/]")

        panel = Panel(
            Align.center(grid),
            title="[bold green]🛡️ Architecture Clean[/]",
            border_style="green",
            box=box.ROUNDED,
            padding=(1, 2),
            expand=False
        )
        console.print(panel)
        console.print()
        return

    # --- FAILURE STATE ---
    # 1. Summary Header
    summary_grid = Table.grid(padding=(0, 2))
    summary_grid.add_column(style="dim", justify="right")
    summary_grid.add_column(style="bold white")
    
    summary_grid.add_row("Files Scanned:", f"{response_dto.total_scanned}")
    summary_grid.add_row("Violations:", f"[red]{len(response_dto.violations)}[/]")
    summary_grid.add_row("Status:", "[bold red]FAILED[/]")

    summary_panel = Panel(
        Align.center(summary_grid),
        title="[bold red]❌ Architectural Violations Found[/]",
        border_style="red",
        box=box.ROUNDED,
        expand=False
    )
    console.print(summary_panel)
    console.print()

    # 2. Detailed Table (Existing logic, slightly tweaked style)
    table = Table(
        box=box.SIMPLE_HEAD, 
        expand=True, 
        border_style="dim red",
        header_style="bold red"
    )
    table.add_column("Rule", width=6)
    table.add_column("Context", width=12, style="dim")
    table.add_column("Violation Details")
    
    for v in response_dto.violations:
        # Formatting the location nicely
        loc = f"[bold white]{v.source}[/] [red]→[/] [dim white]{v.target}[/]"
        msg = f"{v.message}\nLoc: {loc}"
        
        table.add_row(
            v.rule_id, 
            v.target_context if v.target_context else "internal",
            msg
        )
    
    console.print(table)
    console.print()