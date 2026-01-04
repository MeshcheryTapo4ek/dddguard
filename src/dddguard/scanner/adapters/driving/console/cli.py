import shutil
import json
import typer
from pathlib import Path
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
    DirectionEnum,
)

from ....ports.driving import ScannerController, ScanResponseSchema, ClassifiedNodeSchema

# Local Adapters
from .scan_options import ScanOptions
from .wizard import ScanSettingsWizard
from .session_state import set_last_scan_options, get_last_scan_options

console = Console()


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


# --- INTERNAL FLOWS (Adapter Logic) ---


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
        # We pass the wizard options directly to the controller
        schema: ScanResponseSchema = controller.scan_project(
            target_path=opts.target_path,
            whitelist_contexts=opts.contexts,
            whitelist_layers=opts.layers,
            dirs_only=opts.dirs_only,
            scan_all=opts.scan_all,
            import_depth=opts.import_depth,
        )

        # 5. Handle Side Effects (Saving Report)
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


def _render_classified_tree(root_node: ClassifiedNodeSchema):
    """
    Renders the architecture as a detailed table.
    Columns: [Macro] [Context] [Layer] [Dir] | Tree | [Type] [Method]
    """
    
    # --- 1. Setup Table ---
    table = Table(
        box=box.SIMPLE_HEAD, 
        show_header=True, 
        header_style="bold white",
        expand=True,
        padding=(0, 1)
    )
    
    # Metadata Columns (Left)
    table.add_column("Macro", style="dim", width=10, no_wrap=True)
    table.add_column("Context", style="dim", width=12, no_wrap=True)
    table.add_column("Layer", style="dim", width=12, no_wrap=True)
    table.add_column("Dir", style="dim", width=3, justify="center")
    
    # Structure (Center)
    table.add_column(f"Structure ({root_node.name})", no_wrap=True, )
    
    # Details (Right)
    table.add_column("Type", style="bold", width=15)
    
    table.add_column("Method", justify="left", min_width=10)

    # --- 2. Helper Logic ---

    def _pick_color(name: str) -> str:
        """Deterministically picks a distinct color for a given name."""
        if not name or name == "Default":
            return "dim white"
            
        # Distinct palette avoiding very dark colors
        palette = [
            "cyan", "magenta", "green", "yellow", 
            "blue", "orange1", "plum1", "gold1", 
            "spring_green1", "deep_sky_blue1"
        ]
        # Simple hash to pick index
        idx = sum(ord(c) for c in name) % len(palette)
        return palette[idx]

    def get_layer_color(layer: LayerEnum) -> str:
        colors = {
            LayerEnum.DOMAIN: "dodger_blue1",
            LayerEnum.APP: "medium_purple1",
            LayerEnum.PORTS: "sky_blue1",
            LayerEnum.ADAPTERS: "green3",
            LayerEnum.COMPOSITION: "gold1",
            LayerEnum.GLOBAL: "grey62",
            LayerEnum.UNDEFINED: "red",
        }
        return colors.get(layer, "white")

    def format_method(method: MatchMethod) -> str:
        # FIX: Returning full names instead of abbreviations
        if method == MatchMethod.STRUCTURAL:
            return "[green]STRUCTURAL[/]" 
        if method == MatchMethod.NAME:
            return "[blue]NAME[/]"
        return "[red]UNKNOWN[/]"

    def format_layer_cell(passport) -> Text:
        """Formats the Layer column with full name (e.g., DOMAIN)."""
        if passport.layer == LayerEnum.UNDEFINED:
            return Text("---", style="dim red")
            
        color = get_layer_color(passport.layer)
        return Text(passport.layer.value, style=color)

    def format_direction_cell(passport) -> Text:
        """Formats direction (In/Out)."""
        if passport.direction == DirectionEnum.DRIVING:
            return Text("In", style="green")
        if passport.direction == DirectionEnum.DRIVEN:
            return Text("Out", style="orange1")
        return Text("", style="dim")

    def format_macro_cell(passport) -> Text:
        """Macro Zone with unique color."""
        name = passport.macro_zone
        if not name or name == "General":
            return Text("Default", style="dim")
        
        color = _pick_color(name)
        return Text(name.upper(), style=f"bold {color}")

    def format_context_cell(passport) -> Text:
        """Context Name with unique color."""
        name = passport.context_name
        if not name:
            return Text("-", style="dim")
            
        color = _pick_color(name)
        return Text(name, style=color)

    # --- 3. Recursive Flattener ---
    
    def add_nodes_recursive(node: ClassifiedNodeSchema, prefix: str = "", is_last: bool = True, is_root: bool = False):
        # Determine Tree Branch Character
        connector = ""
        if not is_root:
            connector = "└── " if is_last else "├── "
        
        # --- Build Row Data ---
        
        # Col 1: Macro
        macro_cell = format_macro_cell(node.passport)

        # Col 2: Context
        ctx_cell = format_context_cell(node.passport)
        
        # Col 3: Layer
        layer_cell = format_layer_cell(node.passport)

        # Col 4: Direction
        dir_cell = format_direction_cell(node.passport)
        
        # Col 5: Tree Structure
        tree_text = Text(prefix + connector, style="dim white")
        name_style = "bold white" if node.is_dir else "white"
        tree_text.append(node.name, style=name_style)
        if node.is_dir:
            tree_text.append("/", style="dim white")
            
        # Col 6: Component Type
        type_str = str(node.passport.component_type).split(".")[-1]
        type_color = get_layer_color(node.passport.layer)
        
        if node.passport.layer == LayerEnum.UNDEFINED and not node.is_dir:
             type_cell = Text("UNKNOWN", style="bold red")
        elif node.is_dir:
             type_cell = Text("") 
        else:
             type_cell = Text(type_str, style=type_color)

        # Col 7: Method
        method_cell = format_method(node.passport.match_method) if not node.is_dir else ""

        # Add Row
        table.add_row(
            macro_cell, 
            ctx_cell, 
            layer_cell, 
            dir_cell, 
            tree_text, 
            type_cell, 
            method_cell
        )

        # --- Recurse ---
        children_count = len(node.children)
        for index, child in enumerate(node.children):
            is_last_child = (index == children_count - 1)
            
            # Calculate next prefix
            next_prefix = prefix
            if not is_root:
                next_prefix += "    " if is_last else "│   "
            
            add_nodes_recursive(child, next_prefix, is_last_child, is_root=False)

    # --- 4. Execute & Print ---
    add_nodes_recursive(root_node, is_root=True)
    
    console.print()
    console.print(table)
    console.print()