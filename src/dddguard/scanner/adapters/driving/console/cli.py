import shutil
import json
import typer
from pathlib import Path
from rich.tree import Tree
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.align import Align
from rich.text import Text

# Shared Infrastructure
from dddguard.shared import (
    render_config_info,
    SCANNER_THEME,
    ask_path,
    print_no_config_warning,
    safe_execution,
    YamlConfigLoader,
    LayerEnum,
    MatchMethod,
)
from ....ports.driving.scanner_controller import (
    ScannerController,
    ScanResponseSchema,
    ClassifiedNodeSchema,
)

# Local Adapters
from .scan_options import ScanOptions
from .wizard import ScanSettingsWizard
# CHANGED: Import from session_state instead of scan_history
from .session_state import set_last_scan_options, get_last_scan_options

console = Console()

# CLASSIFICATION:
# Scope: BOUNDED CONTEXT (Scanner)
# Layer: ADAPTERS
# Direction: DRIVING
# Type: CLI (Entrypoint)


def register_commands(app: typer.Typer, controller: ScannerController):
    """
    Registers commands for the Scanner Context.
    Injects the ScannerController (Port) as the handler for business logic.
    """

    @app.command(name="scandir")
    def scandir(
        depth: int = typer.Option(0, help="Recursively include imported modules up to depth."),
    ):
        """Interactive directory scanner."""
        run_scan_directory_flow(controller, depth)

    @app.command(name="scan")
    def scan(
        depth: int = typer.Option(0, help="Recursively include imported modules up to depth."),
    ):
        """Project scanner (uses config)."""
        run_scan_project_flow(controller, depth)

    @app.command(name="classify")
    def classify():
        """🔍 Visualize project architecture tree."""
        run_classify_project_flow(controller)

    @app.command(name="classifydir")
    def classifydir():
        """🔍 Visualize directory architecture tree."""
        run_classify_directory_flow(controller)


# --- INTERNAL FLOWS (Adapter Logic - Now Public for Root Usage) ---


def run_scan_directory_flow(controller: ScannerController, import_depth: int = 0):
    # 1. Ask for path (Adapter IO)
    target_path = ask_path(
        message="Select directory to scan",
        default=".",
        must_exist=True,
        theme=SCANNER_THEME,
    )
    if not target_path:
        return

    # 2. Init Wizard (Adapter UI)
    options = ScanOptions(target_path=target_path, import_depth=import_depth)
    wizard = ScanSettingsWizard(options, controller.config)

    # 3. Run Wizard
    if wizard.run():
        _execute_scan(controller, options)


def run_scan_project_flow(controller: ScannerController, import_depth: int = 0):
    loader = YamlConfigLoader()
    config_path = loader._discover_config_file()

    if config_path is None:
        print_no_config_warning()
        run_scan_directory_flow(controller, import_depth)
        return

    render_config_info(controller.config, theme=SCANNER_THEME)

    options = ScanOptions(
        target_path=controller.config.project.absolute_source_path,
        scan_all=False,
        import_depth=import_depth,
    )

    wizard = ScanSettingsWizard(options, controller.config)
    if wizard.run():
        _execute_scan(controller, options)


def run_repeat_last_scan_flow(controller: ScannerController):
    """
    Immediately executes the last scan without the wizard.
    """
    # CHANGED: Use in-memory getter
    last_opts = get_last_scan_options()
    if not last_opts:
        console.print("[red]❌ No previous scan history found in this session.[/]")
        return

    console.print(f"[dim]Repeating scan for: {last_opts.target_path}[/]")
    _execute_scan(controller, last_opts)


def _execute_scan(controller: ScannerController, opts: ScanOptions):
    """
    Bridges the Adapter State to the Port Call.
    """
    mode_msg = "ALL files" if opts.scan_all else "Python files"
    depth_msg = f", depth={opts.import_depth}" if opts.import_depth > 0 else ""

    with safe_execution(status_msg=f"Scanning... ({mode_msg}{depth_msg})"):
        # 4. CALL PORT (Controller)
        schema: ScanResponseSchema = controller.scan_project(
            target_path=opts.target_path,
            whitelist_contexts=opts.contexts,
            whitelist_layers=opts.layers,
            dirs_only=opts.dirs_only,
            scan_all=opts.scan_all,
            import_depth=opts.import_depth,
        )

        # 5. Handle Side Effects
        with open(opts.output_json, "w", encoding="utf-8") as f:
            json.dump(schema.source_tree, f, indent=2, ensure_ascii=False)

    # 6. Save History (In-Memory)
    set_last_scan_options(opts)

    # 7. Render Output (Adapter UI) & Pause
    _render_success_report(schema, opts.output_json)
    
    # PAUSE implementation
    console.input("[dim]Press Enter to return to menu...[/]")


def run_classify_project_flow(controller: ScannerController):
    with safe_execution(status_msg="Analyzing architecture structure..."):
        # CALL PORT
        tree_schema = controller.classify_tree()

    _render_classified_tree(tree_schema)
    console.input("[dim]Press Enter to return to menu...[/]")


def run_classify_directory_flow(controller: ScannerController):
    target = ask_path(message="Select directory to classify", theme=SCANNER_THEME)
    if not target:
        return

    with safe_execution(status_msg="Analyzing directory structure..."):
        # CALL PORT
        tree_schema = controller.classify_tree(target)

    _render_classified_tree(tree_schema)
    console.input("[dim]Press Enter to return to menu...[/]")


# --- RENDER HELPERS (Rich UI) ---


def _render_success_report(dto: ScanResponseSchema, output_file: Path):
    grid = Table.grid(padding=(0, 2))
    grid.add_column(style="dim", justify="right")
    grid.add_column(style="bold white")

    grid.add_row("Contexts Found:", f"[cyan]{dto.context_count}[/]")
    grid.add_row("Modules Found:", f"[cyan]{dto.file_count}[/]")
    
    unclass_color = "red" if dto.unclassified_count > 0 else "green"
    grid.add_row("Unclassified:", f"[{unclass_color}]{dto.unclassified_count}[/]")
    
    grid.add_row("Snapshot Size:", f"[green]{dto.snapshot_file_count}[/]")

    grid.add_row("", "")
    grid.add_row("Output File:", f"[green]{output_file}[/]")

    panel = Panel(
        Align.center(grid),
        title="[bold green]✅ Scan Completed Successfully[/]",
        border_style="green",
        box=box.ROUNDED,
        padding=(1, 2),
        expand=False,
    )
    console.print()
    console.print(panel)
    console.print()


def _render_classified_tree(dto: ClassifiedNodeSchema):
    width = shutil.get_terminal_size((100, 20)).columns
    tree = Tree(f"[bold cyan]SOURCE ROOT[/] ({dto.name})")

    def get_color(passport) -> str:
        if (
            passport.match_method == MatchMethod.UNKNOWN
            or passport.layer == LayerEnum.UNDEFINED
        ):
            return "red"
        colors = {
            LayerEnum.DOMAIN: "dodger_blue1",
            LayerEnum.APP: "medium_purple1",
            LayerEnum.PORTS: "sky_blue1",
            LayerEnum.ADAPTERS: "green3",
            LayerEnum.COMPOSITION: "gold1",
            LayerEnum.GLOBAL: "grey62",
        }
        return colors.get(passport.layer, "white")

    def format_passport_tag(p) -> Text:
        color = get_color(p)
        method = "S" if p.match_method == MatchMethod.STRUCTURAL else "N"
        if p.match_method == MatchMethod.UNKNOWN:
            method = "?"

        type_name = str(p.component_type).split(".")[-1][:10]
        layer_name = str(p.layer.value)[:3].upper()

        tag = Text.assemble(
            (f" {method} ", f"on {color} reverse"),
            (f" {type_name} ", f"bold {color}"),
            (f" {p.direction.value[:3]} ", "dim"),
            (f" {layer_name} ", "italic grey62"),
            (f" {p.context_name or '---'} ", "grey37"),
        )
        return tag

    def add_branches(node_dto: ClassifiedNodeSchema, rich_node: Tree, depth: int = 0):
        for child in node_dto.children:
            label = Text(child.name)
            if child.is_dir:
                label.stylize("bold blue")

            branch = rich_node.add(label)

            if not child.is_dir:
                passport_tag = format_passport_tag(child.passport)
                current_line_len = len(child.name) + (depth * 4) + 4
                padding_size = width - current_line_len - 35

                label.append(" " * max(1, padding_size))
                label.append(passport_tag)

            add_branches(child, branch, depth + 1)

    add_branches(dto, tree)
    console.print(tree)