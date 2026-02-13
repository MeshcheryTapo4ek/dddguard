from pathlib import Path

import typer
from rich import box
from rich.table import Table

# --- UI IMPORTS ---
from dddguard.shared.adapters.driving import (
    LINTER_THEME,
    tui,  # Unified TUI
)
from dddguard.shared.assets.asset_help import get_linter_help_renderable

from ...ports.driving import LinterFacade, LinterResponseSchema, RulesMatrixSchema

# --- LOCAL ADAPTERS (Wizards) ---
from .lint_wizard import LintSettingsWizard
from .rules_viewer import RulesViewer


def register_commands(app: typer.Typer, facade: LinterFacade) -> None:
    """
    Registers Linter commands.
    """

    @app.command(name="lintdir")
    def lintdir() -> None:
        """Lint a SPECIFIC directory."""
        run_lint_directory_flow(facade)

    @app.command(name="lint")
    def lint(
        auto: bool = typer.Option(
            False,
            "--auto",
            "-a",
            help="Run automatically without interactive wizard (for CI/CD)",
        ),
    ) -> None:
        """Lint project architecture."""
        run_lint_project_flow(facade, auto=auto)


# --- PUBLIC FLOWS ---


def run_lint_directory_flow(facade: LinterFacade) -> None:
    tui.set_theme(LINTER_THEME)
    target: Path | None = tui.path(message="Select directory to lint")
    if not target:
        return

    _run_lint_logic(facade, target)


def run_lint_project_flow(facade: LinterFacade, auto: bool = False) -> None:
    tui.set_theme(LINTER_THEME)
    config = facade.config

    if config.project.config_file_path is None:
        tui.warning("Configuration Missing", "Using default source path.")

    target = config.project.absolute_source_path

    if auto:
        # Non-interactive mode: run directly without wizard
        _run_lint_direct(facade, target)
    else:
        _run_lint_logic(facade, target)


def _run_lint_direct(facade: LinterFacade, path: Path) -> None:
    """
    Non-interactive linting for CI/CD.
    Runs directly without wizard.
    """
    # Execute Scan via Port
    with tui.spinner("Checking architecture..."):
        response: LinterResponseSchema = facade.lint_project(path)

    # Render Report (Adapter Responsibility) without pause
    _print_report(response, auto_mode=True)

    # Exit with error code if violations found
    if not response.success:
        raise typer.Exit(1)


def _run_lint_logic(facade: LinterFacade, path: Path) -> None:
    wizard = LintSettingsWizard(facade.config)

    # Wizard Loop
    while True:
        result: bool | str = wizard.run()

        if result is False:
            return

        if result == "view_summary":
            tui.clear()
            tui.console.print(get_linter_help_renderable())
            tui.pause()
            continue

        if result == "view_matrix":
            # Adapter asks Port for data to visualize
            rules_matrix: RulesMatrixSchema = facade.get_rules_matrix()
            viewer = RulesViewer(rules_matrix)
            viewer.render()
            continue

        if result is True:  # Run
            break

    # Execute Scan via Port
    with tui.spinner("Checking architecture..."):
        response: LinterResponseSchema = facade.lint_project(path)

    # Render Report (Adapter Responsibility)
    _print_report(response)


def _print_report(response_dto: LinterResponseSchema, auto_mode: bool = False) -> None:
    if response_dto.success:
        # --- SUCCESS STATE ---
        tui.success(
            "Architecture Clean",
            {
                "Files Scanned": str(response_dto.total_scanned),
                "Violations": "[green]0[/]",
                "Status": "[bold green]PASSED[/]",
            },
        )
        if not auto_mode:
            tui.pause()
        return

    # --- FAILURE STATE ---
    tui.error(
        "Architectural Violations Found",
        {
            "Files Scanned": str(response_dto.total_scanned),
            "Violations": f"[red]{len(response_dto.violations)}[/]",
            "Status": "[bold red]FAILED[/]",
        },
    )

    # Detailed Table
    table = Table(
        box=box.SIMPLE_HEAD,
        expand=True,
        border_style="dim red",
        header_style="bold red",
    )
    table.add_column("Rule", width=6)
    table.add_column("Context", width=12, style="dim")
    table.add_column("Violation Details")

    for v in response_dto.violations:
        loc = f"[bold white]{v.source}[/] [red]->[/] [dim white]{v.target}[/]"
        msg = f"{v.message}\nLoc: {loc}"

        table.add_row(v.rule_name, v.target_context or "internal", msg)

    tui.console.print(table)
    tui.console.print()

    if not auto_mode:
        tui.pause()
