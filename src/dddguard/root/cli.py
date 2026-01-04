import typer
from pathlib import Path
from rich.console import Console

# --- UI IMPORTS ---
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator

# Shared Infrastructure
from dddguard.shared import (
    render_dashboard,
    ask_select,
    YamlConfigLoader,
    safe_execution,
    ROOT_THEME,
)

# --- Dependency Injection ---
from dddguard.scanner import ScannerContainer
from dddguard.scaffolder import ScaffolderContainer
from dddguard.linter import LinterContainer
from dddguard.visualizer import VisualizerContainer

from .composition import build_app_container

# --- Import FLOWS from Adapters ---
from dddguard.scanner.adapters.driving import (
    run_scan_project_flow,
    run_scan_directory_flow,
    run_classify_project_flow,
    run_classify_directory_flow,
    run_repeat_last_scan_flow, 
    get_last_scan_options, 
)
from dddguard.linter.adapters.driving import (
    run_lint_project_flow,
    run_lint_directory_flow,
)
from dddguard.visualizer.adapters.driving import (
    run_viz_project_flow,
    run_viz_directory_flow
)

console = Console()
app = typer.Typer(
    help="DDDGuard: Architecture Guard & Linter for DDD projects.",
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
            console.print("[yellow]↻ Reloading Configuration...[/]", style="dim")
            continue
        except Exception:
            # Catch errors during container build or menu loop
            console.print("\n[bold red]❌ Critical Application Error[/bold red]")
            console.print_exception(show_locals=False)
            break


def _interactive_menu(container) -> None:
    # Retrieve Controllers/Facades from DI
    scanner_ctrl = container.get(ScannerContainer).controller
    scaffolder_ctrl = container.get(ScaffolderContainer).controller
    linter_ctrl = container.get(LinterContainer).controller
    visualizer_ctrl = container.get(VisualizerContainer).controller

    loader = YamlConfigLoader()

    def item(label: str, desc: str) -> str:
        return f"{label:<20} {desc}"

    while True:
        console.clear()
        config_path = loader._discover_config_file()
        config_exists = config_path is not None

        if config_exists:
            current_config = loader.load(config_path)
        else:
            current_config = scanner_ctrl.config

        render_dashboard(
            current_config, config_path, theme=ROOT_THEME, show_context=False
        )

        choices = []
        
        # --- DYNAMIC HISTORY CHECK (In-Memory) ---
        last_scan = get_last_scan_options()
        if last_scan:
            target_name = last_scan.target_path.name
            choices.append(
                Choice(
                    "REPEAT_SCAN", 
                    f"0. Repeat Scan:       {target_name}/"
                )
            )
            choices.append(Separator())
        # -----------------------------

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
                    Choice(
                        "INIT_CONFIG", item("Create Config", "Generate config.yaml")
                    ),
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

        action = ask_select(
            message=None,
            choices=choices,
            theme=ROOT_THEME,
            instruction="(Use arrow keys to navigate)",
        )

        if action == "EXIT" or action is None:
            console.print("\n[yellow]Goodbye! 👋[/]")
            return

        try:
            console.print()
            
            # --- ACTION DISPATCH ---
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

            # --- LINTER ACTIONS ---
            elif action == "LINT_PROJECT":
                run_lint_project_flow(linter_ctrl)
            elif action == "LINT_DIR":
                run_lint_directory_flow(linter_ctrl)

            # --- VISUALIZER ACTIONS ---
            elif action == "VIZ_PROJECT":
                run_viz_project_flow(visualizer_ctrl, current_config)
            elif action == "VIZ_DIR":
                run_viz_directory_flow(visualizer_ctrl, current_config)

            # --- SCAFFOLDER ACTIONS ---
            elif action == "INIT_CONFIG":
                target_path = Path.cwd()
                with safe_execution("Initializing Configuration..."):
                    response = scaffolder_ctrl.init_project(target_path)

                if response.success:
                    console.print(f"[green]✅ {response.message}[/]")
                    console.print(f"    Config: [bold white]{response.config_path}[/]")
                    console.print("\n[dim]Reloading menu...[/]")
                else:
                    console.print(f"[bold red]❌ {response.message}[/]")
                    if response.error_details:
                        console.print(f"    Details: {response.error_details}")
                    console.input("[dim]Press Enter to continue...[/]")

        except KeyboardInterrupt:
            console.print("\n[yellow]Action cancelled.[/]")
        except Exception:
            # --- IMPROVED ERROR CATCHING ---
            console.print("\n[bold red]❌ Unexpected Error:[/bold red]")
            # This prints the stack trace nicely using Rich
            console.print_exception(show_locals=False) 
            console.print()
            console.input("[dim]Press Enter to return to menu...[/]")


def main() -> None:
    """Application entry point for CLI command registration."""
    # We moved container build inside the interactive loop or individual commands
    # to handle reloading gracefully.
    
    # Register Scanner Commands
    try:
        container = build_app_container()
        scanner = container.get(ScannerContainer)
        scanner.register_commands(app)

        # Register Scaffolder Commands
        scaffolder = container.get(ScaffolderContainer)
        scaffolder.register_commands(app)

        # Register Linter Commands
        linter = container.get(LinterContainer)
        linter.register_commands(app)
        
        # Register Visualizer Commands
        visualizer = container.get(VisualizerContainer)
        visualizer.register_commands(app)

        app(obj={"container": container})
        
    except Exception:
        console.print("[bold red]❌ Fatal Startup Error[/bold red]")
        console.print_exception()


if __name__ == "__main__":
    main()