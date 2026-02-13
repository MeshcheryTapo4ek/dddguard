import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import typer
from rich import box
from rich.table import Table
from rich.text import Text

# Shared Infrastructure
from dddguard.shared.adapters.driving import (
    SCANNER_THEME,
    tui,
)
from dddguard.shared.domain import (
    CodeGraph,
    ComponentPassport,
    DirectionEnum,
    LayerEnum,
    MatchMethod,
    NodeStatus,
)

from ....ports.driving import ScannerFacade

# Local Adapters
from .scan_options import ScanOptions
from .session_state import get_last_scan_options, set_last_scan_options
from .wizard import ScanSettingsWizard


@dataclass
class RenderNode:
    """Local View Model for rendering the classification tree."""

    name: str
    is_dir: bool
    passport: ComponentPassport | None
    children: list["RenderNode"] = field(default_factory=list)


def register_commands(app: typer.Typer, facade: ScannerFacade):
    @app.command(name="scandir")
    def scandir(
        depth: int = typer.Option(0, help="Recursively include imported modules up to depth."),
    ):
        """Interactive directory scanner."""
        run_scan_directory_flow(facade, depth)

    @app.command(name="scan")
    def scan(
        depth: int = typer.Option(0, help="Recursively include imported modules."),
        # [CHANGED] Removed --shared and --root CLI flags
        assets: bool = typer.Option(True, help="Include Asset/Resource entities."),
        file_tree_only: bool = typer.Option(False, "--file-tree-only", help="Mask content."),
    ):
        """Project scanner (uses config)."""
        run_scan_project_flow(facade, depth, assets, file_tree_only)

    @app.command(name="classify")
    def classify():
        """🔍 Visualize project architecture tree."""
        run_classify_project_flow(facade)

    @app.command(name="classifydir")
    def classifydir():
        """🔍 Visualize directory architecture tree."""
        run_classify_directory_flow(facade)


# --- INTERNAL FLOWS (Adapter Logic) ---


def run_scan_directory_flow(facade: ScannerFacade, import_depth: int = 0):
    tui.set_theme(SCANNER_THEME)
    target_path = tui.path(message="Select directory to scan", default=".")

    if not target_path:
        return

    options = ScanOptions(target_path=target_path, import_depth=import_depth)
    wizard = ScanSettingsWizard(options, facade)
    if wizard.run():
        _execute_scan(facade, options)


def run_scan_project_flow(
    facade: ScannerFacade,
    import_depth: int = 0,
    include_assets: bool = True,
    file_tree_only: bool = False,
):
    tui.set_theme(SCANNER_THEME)
    has_config = facade.config.project.absolute_source_path is not None

    if not has_config:
        tui.warning("Configuration Missing", "No config.yaml. Using defaults.")
        # Fallback to dir flow if no config found (simplification)
        run_scan_directory_flow(facade, import_depth)
        return

    config = facade.config

    # Just a quick check to ensure we start wizard at project root
    options = ScanOptions(
        target_path=config.project.absolute_source_path,
        scan_all=False,
        import_depth=import_depth,
        include_assets=include_assets,
        file_tree_only=file_tree_only,
    )

    wizard = ScanSettingsWizard(options, facade)
    if wizard.run():
        _execute_scan(facade, options)


def run_repeat_last_scan_flow(facade: ScannerFacade):
    """
    Immediately executes the last scan without the wizard.
    """
    last_opts = get_last_scan_options()
    if not last_opts:
        tui.error("No Scan History", "No previous scan found in this session.")
        return

    tui.console.print(f"[dim]Repeating scan for: {last_opts.target_path}[/]")
    _execute_scan(facade, last_opts)


def _execute_scan(facade: ScannerFacade, opts: ScanOptions):
    """
    Bridges the Adapter State to the Port Call.
    """
    mode_msg = "ALL files" if opts.scan_all else "Python files"
    depth_msg = f", depth={opts.import_depth}" if opts.import_depth > 0 else ""

    with tui.spinner(f"Scanning... ({mode_msg}{depth_msg})"):
        # 1. CALL PORT (Facade)
        # [CHANGED] Simplified call, removed deprecated flags
        graph: CodeGraph = facade.scan_project(
            target_path=opts.target_path,
            whitelist_contexts=opts.contexts,
            whitelist_layers=opts.layers,
            scan_all=opts.scan_all,
            import_depth=opts.import_depth,
            include_assets=opts.include_assets,
        )

        # 2. Handle Side Effects (Saving Report)
        # Pass the masking flag to the serializer
        tree_view = _graph_to_json_tree(graph, mask_content=opts.file_tree_only)

        with opts.output_json.open("w", encoding="utf-8") as f:
            json.dump(tree_view, f, indent=2, ensure_ascii=False, default=str)

    set_last_scan_options(opts)

    tui.success("Scan Completed", {"Output": str(opts.output_json)})
    tui.pause("[dim]Press Enter to return to menu...[/]")


def run_classify_project_flow(facade: ScannerFacade):
    with tui.spinner("Analyzing architecture structure..."):
        graph = facade.classify_tree()
        root_path = facade.config.project.absolute_source_path
        render_tree = _graph_to_render_tree(graph, root_path)

    _render_classified_tree(render_tree)
    tui.pause("[dim]Press Enter to return to menu...[/]")


def run_classify_directory_flow(facade: ScannerFacade):
    tui.set_theme(SCANNER_THEME)
    target = tui.path(message="Select directory to classify")
    if not target:
        return

    with tui.spinner("Analyzing directory structure..."):
        graph = facade.classify_tree(target)
        render_tree = _graph_to_render_tree(graph, target)

    _render_classified_tree(render_tree)
    tui.pause("[dim]Press Enter to return to menu...[/]")


# --- VIEW LOGIC HELPERS ---


def _graph_to_json_tree(graph: CodeGraph, mask_content: bool) -> dict[str, Any]:
    """
    Reconstructs a nested dictionary directory tree from flat graph paths.
    Applies content masking if requested.
    """
    tree: dict[str, Any] = {}

    for path, node in graph.nodes.items():
        # Only show finalized (visible) nodes
        if node.status != NodeStatus.FINALIZED:
            continue

        parts = path.split(".")
        # Handle empty path (root __init__)
        if path == "":
            parts = []

        # Explicitly include __init__.py in JSON path parts
        if node.file_path and node.file_path.name == "__init__.py":
            parts.append("__init__.py")

        current = tree

        for i, part in enumerate(parts):
            is_last = i == len(parts) - 1

            if part not in current:
                current[part] = {}

            # Handle mixing dicts and leaf values
            if current[part] is None or isinstance(current[part], str):
                if not isinstance(current[part], dict):
                    current[part] = {}

            if is_last:
                if mask_content:
                    current[part] = "<Masked Content>"
                else:
                    current[part] = node.content if node.content is not None else ""
            else:
                current = current[part]

    return tree


def _graph_to_render_tree(graph: CodeGraph, root_path: Path) -> RenderNode:
    """Reconstructs the RenderNode tree for CLI visualization."""
    root_name = root_path.name
    root_node = RenderNode(
        name=root_name,
        is_dir=True,
        passport=None,
        children=[],
    )

    node_lookup = {}
    for path, node in graph.nodes.items():
        parts = list(path.split("."))
        if path == "":
            parts = []

        # Explicitly visualize __init__.py
        if node.file_path and node.file_path.name == "__init__.py":
            parts.append("__init__.py")

        # Skip empty parts if any (e.g. root without init)
        parts = [p for p in parts if p]

        node_lookup[tuple(parts)] = node

    trie: dict[str, Any] = {}
    for parts, node in node_lookup.items():
        cursor = trie
        for part in parts:
            if part not in cursor:
                cursor[part] = {}
            cursor = cursor[part]
        cursor["__node__"] = node

    def build_children(cursor_dict: dict, prefix: str) -> list[RenderNode]:
        children = []
        for name, sub in cursor_dict.items():
            if name == "__node__":
                continue

            node = sub.get("__node__")

            # Logic for determination of is_dir
            has_children = any(k != "__node__" for k in sub)
            is_dir = has_children

            # If it's a leaf node in the trie, it's a file
            if not is_dir and node:
                is_dir = False

            passport = node.passport if node else None

            child_node = RenderNode(
                name=name,
                is_dir=is_dir,
                passport=passport,
                children=build_children(sub, f"{prefix}/{name}" if prefix else name),
            )
            children.append(child_node)

        # Sort: Directories first, then files alphabetically
        return sorted(children, key=lambda x: (not x.is_dir, x.name))

    root_node.children.extend(build_children(trie, ""))
    return root_node


def _render_classified_tree(root_node: RenderNode):
    """
    Renders the architecture as a detailed table.
    Visualizes ComponentPassport data.
    """
    table = Table(
        box=box.SIMPLE_HEAD,
        show_header=True,
        header_style="bold white",
        expand=True,
        padding=(0, 1),
    )

    table.add_column("Macro", style="dim", width=10, no_wrap=True)
    table.add_column("Context", style="dim", width=12, no_wrap=True)
    table.add_column("Layer", style="dim", width=12, no_wrap=True)
    table.add_column("Dir", style="dim", width=3, justify="center")
    table.add_column(f"Structure ({root_node.name})", no_wrap=True)
    table.add_column("Type", style="bold", width=15)
    table.add_column("Method", justify="left", min_width=10)

    # --- Coloring Helpers ---
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
        if method == MatchMethod.STRUCTURAL:
            return "[green]STRUCTURAL[/]"
        if method == MatchMethod.NAME:
            return "[blue]NAME[/]"
        return "[red]UNKNOWN[/]"

    def format_direction_cell(passport) -> Text:
        if not passport:
            return Text("", style="dim")
        if passport.direction == DirectionEnum.DRIVING:
            return Text("In", style="green")
        if passport.direction == DirectionEnum.DRIVEN:
            return Text("Out", style="orange1")
        return Text("-", style="dim")

    def _pick_color(name: str) -> str:
        if not name or name == "Default":
            return "dim white"
        palette = ["cyan", "magenta", "green", "yellow", "blue", "orange1"]
        return palette[sum(ord(c) for c in name) % len(palette)]

    # --- Recursive Renderer ---
    def add_nodes_recursive(
        node: RenderNode, prefix: str = "", is_last: bool = True, is_root: bool = False
    ):
        connector = ""
        if not is_root:
            connector = "└── " if is_last else "├── "

        p = node.passport

        # Cells
        macro_cell = (
            Text(p.macro_zone.upper(), style=f"bold {_pick_color(p.macro_zone)}")
            if p and p.macro_zone
            else Text("")
        )
        ctx_cell = (
            Text(p.context_name, style=_pick_color(p.context_name))
            if p and p.context_name
            else Text("")
        )

        layer_cell = Text("-", style="dim")
        if p and p.layer != LayerEnum.UNDEFINED:
            layer_cell = Text(p.layer.value, style=get_layer_color(p.layer))

        dir_cell = format_direction_cell(p)

        tree_text = Text(prefix + connector, style="dim white")
        tree_text.append(node.name, style="bold white" if node.is_dir else "white")
        if node.is_dir:
            tree_text.append("/", style="dim white")

        type_cell = Text("")
        if p and not node.is_dir:
            if p.layer == LayerEnum.UNDEFINED:
                type_cell = Text("UNKNOWN", style="bold red")
            else:
                t_str = str(p.component_type).split(".")[-1]
                type_cell = Text(t_str, style=get_layer_color(p.layer))

        method_cell = format_method(p.match_method) if p and not node.is_dir else ""

        table.add_row(
            macro_cell,
            ctx_cell,
            layer_cell,
            dir_cell,
            tree_text,
            type_cell,
            method_cell,
        )

        count = len(node.children)
        for i, child in enumerate(node.children):
            is_last_child = i == count - 1
            next_prefix = prefix
            if not is_root:
                next_prefix += "    " if is_last else "│   "
            add_nodes_recursive(child, next_prefix, is_last_child, False)

    add_nodes_recursive(root_node, is_root=True)
    tui.console.print()
    tui.console.print(table)
    tui.console.print()
