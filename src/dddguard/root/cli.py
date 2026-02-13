import sys
import traceback
from pathlib import Path

import typer

# --- UI IMPORTS ---
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator

from dddguard.linter.adapters.driving import (
    run_lint_directory_flow,
    run_lint_project_flow,
)
from dddguard.linter.provider import LinterContainer
from dddguard.scaffolder.provider import ScaffolderContainer

# --- Import FLOWS ---
from dddguard.scanner.adapters.driving import (
    get_last_scan_options,
    run_classify_directory_flow,
    run_classify_project_flow,
    run_repeat_last_scan_flow,
    run_scan_directory_flow,
    run_scan_project_flow,
)

# --- Dependency Injection ---
from dddguard.scanner.provider import ScannerContainer
from dddguard.shared.adapters.driven.yaml_config_loader import YamlConfigLoader

# Shared Infrastructure
from dddguard.shared.adapters.driving import (
    ROOT_THEME,
    tui,
)
from dddguard.visualizer.adapters.driving import (
    run_viz_directory_flow,
    run_viz_project_flow,
)
from dddguard.visualizer.provider import VisualizerContainer

from .composition import build_app_container

app = typer.Typer(
    help="DDDGuard: Architecture Guard & Linter & Scanner for DDD projects.",
    no_args_is_help=False,
    invoke_without_command=True,
)


class ReloadAppSignal(Exception):
    pass


@app.callback()
def main_callback(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        _interactive_menu_loop()


def _interactive_menu_loop() -> None:
    while True:
        try:
            container = build_app_container()
            _interactive_menu(container)
            break
        except ReloadAppSignal:
            tui.console.print("[yellow]↻ Reloading Configuration...[/]", style="dim")
            continue
        except Exception:
            tui.console.print("\n[bold red]Critical Application Error[/bold red]")
            tui.console.print_exception(show_locals=False)
            traceback.print_exc(file=sys.stderr)
            tui.console.print(
                "[dim]Report at: [link]https://github.com/MeshcheryTapo4ek/dddguard/issues[/][/]"
            )
            break


def _interactive_menu(container) -> None:
    # Retrieve facades
    scanner_ctrl = container.get(ScannerContainer).facade
    scaffolder_ctrl = container.get(ScaffolderContainer).facade
    linter_ctrl = container.get(LinterContainer).facade
    visualizer_ctrl = container.get(VisualizerContainer).facade

    loader = YamlConfigLoader()
    tui.set_theme(ROOT_THEME)

    def item(label: str, desc: str) -> str:
        return f"{label:<20} {desc}"

    while True:
        tui.clear()
        config_path = loader._discover_config_file()
        config_exists = config_path is not None

        if config_exists:
            current_config = loader.load(config_path)
        else:
            current_config = scanner_ctrl.config

        # RENDER DASHBOARD VIA TUI
        root = current_config.project.project_root
        src = getattr(current_config.project, "source_dir", "src")

        dashboard_data = {
            "Project": root.name if root else "N/A",
            "Source": src,
            "Config": config_path.name if config_path else "None",
        }

        tui.dashboard(
            title="DDDGuard Architecture Suite",
            subtitle=f"Context: {ROOT_THEME.name}",
            data=dashboard_data,
        )

        choices: list[Choice | Separator] = []

        # --- DYNAMIC HISTORY CHECK ---
        last_scan = get_last_scan_options()
        if last_scan:
            target_name = last_scan.target_path.name
            choices.append(Choice("REPEAT_SCAN", f"0. Repeat Scan:       {target_name}/"))
            choices.append(Separator())

        if config_exists:
            choices.extend(
                [
                    Separator(" PRIMARY PROJECT ACTIONS "),
                    Choice(
                        "SCAN_PROJECT",
                        item("1. Scan Project", "Auto-scan configured source"),
                    ),
                    Choice(
                        "LINT_PROJECT",
                        item("2. Lint Project", "Validate architecture rules"),
                    ),
                    Choice(
                        "VIZ_PROJECT",
                        item("3. Draw Arch", "Generate diagrams from config"),
                    ),
                    Choice(
                        "CLASSIFY_PROJECT",
                        item("4. Classify Tree", "Visualize arch structure"),
                    ),
                    Separator(" DIRECTORY UTILITIES "),
                    Choice(
                        "CLASSIFY_DIR",
                        item("1. Classify Dir", "Visualize specific folder"),
                    ),
                    Choice("VIZ_DIR", item("2. Draw Dir", "Draw specific folder")),
                    Choice("LINT_DIR", item("3. Lint Dir", "Lint specific folder")),
                    Choice("SCAN_DIR", item("4. Scan Dir", "Scan specific folder")),
                ]
            )
        else:
            choices.extend(
                [
                    Separator(" SETUP "),
                    Choice("INIT_CONFIG", item("Create Config", "Generate config.yaml")),
                    Separator(" AD-HOC TOOLS "),
                    Choice(
                        "CLASSIFY_DIR",
                        item("Classify Dir", "Visualize specific folder"),
                    ),
                    Choice("VIZ_DIR", item("Draw Dir", "Draw specific folder")),
                    Choice("LINT_DIR", item("Lint Dir", "Lint specific folder")),
                    Choice("SCAN_DIR", item("Scan Dir", "Scan specific folder")),
                ]
            )

        choices.extend([Separator(), Choice("EXIT", "Exit")])

        action = tui.select(
            message=None,
            choices=choices,
        )

        if action == "EXIT" or action is None:
            tui.console.print("\n[yellow]Goodbye! 👋[/]")
            return

        tui.console.print()

        # --- ACTION DISPATCH (wrapped in error_boundary) ---
        with tui.error_boundary():
            if action == "REPEAT_SCAN":
                run_repeat_last_scan_flow(scanner_ctrl)

            elif action == "SCAN_PROJECT":
                run_scan_project_flow(scanner_ctrl)
            elif action == "CLASSIFY_PROJECT":
                run_classify_project_flow(scanner_ctrl)
            elif action == "SCAN_DIR":
                run_scan_directory_flow(scanner_ctrl)
            elif action == "CLASSIFY_DIR":
                run_classify_directory_flow(scanner_ctrl)

            elif action == "LINT_PROJECT":
                run_lint_project_flow(linter_ctrl)
            elif action == "LINT_DIR":
                run_lint_directory_flow(linter_ctrl)

            elif action == "VIZ_PROJECT":
                run_viz_project_flow(visualizer_ctrl, current_config)
            elif action == "VIZ_DIR":
                run_viz_directory_flow(visualizer_ctrl, current_config)

            elif action == "INIT_CONFIG":
                target_path = Path.cwd()
                with tui.spinner("Initializing Configuration..."):
                    response = scaffolder_ctrl.init_project(target_path)

                if response.success:
                    tui.success(response.message, {"Config": str(response.config_path)})
                    tui.console.print("\n[dim]Reloading menu...[/]")
                else:
                    tui.error(response.message, response.error_details)
                    tui.pause()


def main() -> None:
    try:
        container = build_app_container()
        scanner = container.get(ScannerContainer)
        scanner.register_commands(app)
        scaffolder = container.get(ScaffolderContainer)
        scaffolder.register_commands(app)
        linter = container.get(LinterContainer)
        linter.register_commands(app)
        visualizer = container.get(VisualizerContainer)
        visualizer.register_commands(app)

        app(obj={"container": container})

    except Exception:
        tui.console.print("[bold red]Fatal Startup Error[/bold red]")
        tui.console.print_exception()
        traceback.print_exc(file=sys.stderr)


if __name__ == "__main__":
    main()
