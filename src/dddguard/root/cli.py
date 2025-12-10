import typer
from rich.console import Console

# --- UI IMPORTS ---
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator

from dddguard.shared.ports.driving.ui import (
    render_dashboard, 
    ask_select
)
from dddguard.shared.ports.driving.ui.themes import ROOT_THEME

# --- Dependency Injection ---
from dddguard.scanner import ScannerContainer
from dddguard.linter import LinterContainer
from dddguard.scaffolder import ScaffolderContainer
from dddguard.visualizer import VisualizerContainer
from dddguard.shared.adapters.driven import YamlConfigLoader

from .composition import build_app_container

# --- Import FLOWS from Ports ---
from dddguard.scanner.ports.driving.cli import run_scan_project_flow, run_scan_directory_flow
from dddguard.linter.ports.driving.cli import run_lint_project_flow, run_lint_directory_flow
from dddguard.visualizer.ports.driving.cli import run_viz_project_flow, run_viz_directory_flow
from dddguard.scaffolder.ports.driving.cli import run_create_wizard, run_init_config_routine

console = Console()
app = typer.Typer(
    help="DDDGuard: Architecture Guard & Linter for DDD projects.",
    no_args_is_help=False, 
    invoke_without_command=True
)

class ReloadAppSignal(Exception):
    """
    Signal to rebuild the DI container.
    Used when configuration changes (e.g. init config) require a fresh context.
    """
    pass

@app.callback()
def main_callback(ctx: typer.Context):
    """
    Main entry point. Launches interactive mode if no command provided.
    """
    if ctx.invoked_subcommand is None:
        # Instead of building once, we enter the lifecycle loop
        _interactive_menu_loop()

def _interactive_menu_loop():
    """
    Manages the App Lifecycle: Build Container -> Run Menu -> Rebuild if needed.
    """
    while True:
        # 1. Build Container (Fresh Config Load)
        container = build_app_container()
        
        # 2. Run Menu
        try:
            _interactive_menu(container)
            break # Normal Exit
        except ReloadAppSignal:
            console.print("[yellow]↻ Reloading Configuration...[/]", style="dim")
            # Loop continues -> Container rebuilds -> Config reloaded
            continue 

def _interactive_menu(container):
    """Runs the Adaptive TUI main menu."""
    
    # Resolve Controllers
    scanner_ctrl = container.get(ScannerContainer).controller
    linter_ctrl = container.get(LinterContainer).controller
    scaffolder_c = container.get(ScaffolderContainer)
    visualizer_ctrl = container.get(VisualizerContainer).controller
    
    loader = YamlConfigLoader()
    
    # Helper for menu items alignment
    def item(label, desc):
        return f"{label:<20} {desc}"

    while True:
        console.clear()
        
        # 1. Detect State (Dynamic check on every loop iteration)
        config_path = loader._discover_config_file()
        config_exists = config_path is not None
        
        # Load fresh config for Dashboard display
        if config_exists:
            current_config = loader.load(config_path)
        else:
            current_config = scanner_ctrl.config 
            
        # 2. Render Dashboard
        # Pass ROOT_THEME and hide the context subtitle
        render_dashboard(current_config, config_path, theme=ROOT_THEME, show_context=False)
        
        # 3. Build Menu Choices
        choices = []
        
        if config_exists:
            # --- MODE: CONFIG FOUND ---
            choices.extend([
                Separator(" PROJECT TOOLS "),
                Choice("SCAN_PROJECT", item("Scan Project", "Auto-scan configured source")),
                Choice("LINT_PROJECT", item("Lint Architecture", "Validate rules (strict)")),
                Choice("VIZ_PROJECT",  item("Draw Diagram", "Generate architecture map")),
                
                Separator(" UTILITIES "),
                Choice("SCAFFOLD",     item("Scaffold Component", "Interactive wizard")),
                Choice("SCAN_DIR",     item("Scan Directory", "Scan specific folder")),
            ])
        else:
            # --- MODE: NO CONFIG ---
            choices.extend([
                Separator(" SETUP "),
                Choice("INIT_CONFIG", item("Create Config", "Generate config.yaml")),
                
                Separator(" AD-HOC TOOLS "),
                Choice("SCAN_DIR",    item("Scan Directory", "Scan specific folder")),
                Choice("LINT_DIR",    item("Lint Directory", "Validate specific folder")),
                Choice("VIZ_DIR",     item("Draw Directory", "Draw specific folder")),
                
                Separator(" GENERATORS "),
                Choice("SCAFFOLD",    item("Scaffold Component", "Interactive wizard")),
            ])

        choices.extend([
            Separator(),
            Choice("EXIT", "Exit")
        ])

        # 4. Ask Select
        action = ask_select(
            message=None,
            choices=choices,
            theme=ROOT_THEME,
            instruction="(Use arrow keys to navigate)"
        )

        if action == "EXIT" or action is None:
            console.print("\n[yellow]Goodbye! 👋[/]")
            # Use return to exit the function cleanly
            return

        # 5. Execution Logic
        try:
            console.print() # Spacer
            
            # === SCAFFOLDER ===
            if action == "INIT_CONFIG":
                run_init_config_routine(scaffolder_c.create_config)
                # 🔥 CRITICAL: Trigger Hot Reload to pick up new config
                raise ReloadAppSignal()

            elif action == "SCAFFOLD":
                run_create_wizard(
                    scaffolder_c.create_component,
                    scaffolder_c.list_templates,
                    config_uc=scaffolder_c.create_config
                )

            # --- SCANNER ---
            elif action == "SCAN_PROJECT":
                run_scan_project_flow(scanner_ctrl)
            
            elif action == "SCAN_DIR":
                run_scan_directory_flow(scanner_ctrl)

            # --- LINTER ---
            elif action == "LINT_PROJECT":
                run_lint_project_flow(linter_ctrl)

            elif action == "LINT_DIR":
                run_lint_directory_flow(linter_ctrl)

            # --- VISUALIZER ---
            elif action == "VIZ_PROJECT":
                run_viz_project_flow(visualizer_ctrl, current_config)
            
            elif action == "VIZ_DIR":
                run_viz_directory_flow(visualizer_ctrl, current_config)
        
        except ReloadAppSignal:
            # Propagate up to the loop to trigger rebuild
            raise 
        except KeyboardInterrupt:
            console.print("\n[yellow]Action cancelled.[/]")
        except Exception as e:
            console.print(f"\n[bold red]❌ Unexpected Error:[/bold red] {e}")
        
        # Pause before returning to menu
        console.print()
        console.input("[dim]Press Enter to return to menu...[/]")

def main():
    # Note: When running directly, we build the initial container here
    # just for command registration, but interactive mode rebuilds it.
    container = build_app_container()
    
    scanner = container.get(ScannerContainer)
    linter = container.get(LinterContainer)
    scaffolder = container.get(ScaffolderContainer)
    visualizer = container.get(VisualizerContainer)

    scanner.register_commands(app)
    linter.register_commands(app)
    scaffolder.register_commands(app)
    visualizer.register_commands(app)

    app(obj={"container": container})

if __name__ == "__main__":
    main()