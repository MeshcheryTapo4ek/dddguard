from typing import List, Any, Tuple, Optional
from pathlib import Path
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.rule import Rule
from rich.align import Align

# --- InquirerPy Imports ---
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator

from dddguard.shared.domain import LayerEnum, ConfigVo
from dddguard.shared.adapters.driving import (
    SCANNER_THEME,
    ask_select,
    ask_multiselect,
    ask_text,
)

from .scan_options import ScanOptions

console = Console()


class ScanSettingsWizard:
    """
    Interactive UI Adapter (InquirerPy).
    Configures the ScanOptions object based on user input.
    """

    def __init__(self, options: ScanOptions, config: ConfigVo):
        self.options = options
        self.config = config
        # Filter out technical layers for display
        self.available_layers = [
            layer
            for layer in LayerEnum
            if layer not in (LayerEnum.GLOBAL, LayerEnum.UNDEFINED)
        ]

    def run(self) -> bool:
        """
        Main Event Loop for the Wizard.
        Returns True if the user selected 'Execute', False if cancelled.
        """
        last_pointer_value = "run"

        while True:
            console.clear()
            self._render_dashboard()

            choices = self._build_main_menu_choices()

            action = ask_select(
                message=None,
                choices=choices,
                default=last_pointer_value,
                theme=SCANNER_THEME,
                instruction="",
            )

            # Escape handling
            if action is None or action == "cancel":
                console.clear()
                return False

            if action == "run":
                return True

            self._handle_action(action)
            last_pointer_value = action

    def _handle_action(self, action: str) -> None:
        """Dispatches menu actions to update the mutable options object."""
        opts = self.options

        if action == "toggle_all":
            opts.scan_all = not opts.scan_all
        elif action == "toggle_dirs":
            opts.dirs_only = not opts.dirs_only
        
        # New Action for Depth
        elif action == "edit_depth":
            self._edit_depth_subscreen()

        elif action == "edit_layers":
            self._edit_layers_subscreen()
        elif action == "edit_contexts":
            self._edit_contexts_subscreen()
        elif action == "edit_macros":
            self._edit_macros_subscreen()
        elif action == "check_config":
            self._show_config_subscreen()

    def _render_dashboard(self) -> None:
        """Renders the current scanner state panel using Rich."""
        opts = self.options
        color = SCANNER_THEME.primary_color

        # --- Top Section: Target Path ---
        path_str = str(opts.target_path)
        is_project_root = False
        source_dir_display = "Unknown"

        # Check if we are scanning the configured source root
        if self.config.project:
            if (
                opts.target_path.resolve()
                == self.config.project.absolute_source_path.resolve()
            ):
                is_project_root = True
                source_dir_display = str(self.config.project.source_dir)

        path_text = Text()
        path_text.append("Target: ", style="dim")
        if is_project_root:
            path_text.append("Project Source ", style=f"bold {color}")
            path_text.append(f"({source_dir_display})", style="white")
        else:
            path_text.append(path_str, style=f"bold {color}")

        # --- Grid Section: Settings & Filters ---
        # Left Column: Flags
        settings_table = Table.grid(padding=(0, 2))
        settings_table.add_column(style="dim", justify="right", min_width=10)
        settings_table.add_column(style="bold white")

        # Reordered Display
        settings_table.add_row("Mode:", "All Files" if opts.scan_all else "Python Only")
        
        # Show Depth
        depth_val = f"{opts.import_depth} levels" if opts.import_depth > 0 else "None (Strict)"
        depth_style = "bold yellow" if opts.import_depth > 0 else "dim"
        settings_table.add_row("Imp. Depth:", f"[{depth_style}]{depth_val}[/]")

        settings_table.add_row(
            "Type:", "Directories Only" if opts.dirs_only else "Full Tree"
        )

        # Right Column: Scope & Filters
        filter_table = Table.grid(padding=(0, 2))
        filter_table.add_column(style="dim", justify="right", min_width=10)
        filter_table.add_column(style=f"bold {color}")

        l_count = len(opts.layers) if opts.layers else "ALL"
        c_count = len(opts.contexts) if opts.contexts else "ALL"
        
        filter_table.add_row("Layers:", f"{l_count}")
        
        # Display Macros if active
        if self.config.project.macro_contexts:
            m_count = len(opts.macro_contexts) if opts.macro_contexts else "ALL"
            filter_table.add_row("Macros:", f"{m_count}")

        filter_table.add_row("Contexts:", f"{c_count}")

        grid = Table(box=None, expand=True, padding=0, show_header=False)
        grid.add_column(ratio=5)
        grid.add_column(ratio=5)
        grid.add_row(settings_table, filter_table)

        # --- Assemble Panel ---
        content = Group(Align.center(path_text), Rule(style=f"dim {color}"), grid)

        panel = Panel(
            content,
            title=f"[bold {color}]Scanner Configuration[/]",
            subtitle="[dim]Arrows to navigate • Enter to toggle[/]",
            subtitle_align="right",
            border_style=color,
            padding=(1, 2),
            expand=True,
        )
        console.print(panel)

    def _build_main_menu_choices(self) -> List[Any]:
        opts = self.options
        has_macros = bool(self.config.project.macro_contexts)

        def item(key, label, is_active):
            status = "[ON] " if is_active else "[OFF]"
            return Choice(value=key, name=f"{label:<22} {status}")

        def filter_item(key, label, is_all, count):
            val = "[ALL]" if is_all else f"[{count}]"
            return Choice(value=key, name=f"{label:<22} {val}")
        
        def value_item(key, label, value):
            return Choice(value=key, name=f"{label:<22} [{value}]")

        choices = [
            Separator(" STRATEGY "),
            item("toggle_all", "Scan All Files", opts.scan_all),
            value_item("edit_depth", "Import Depth", opts.import_depth),
            item("toggle_dirs", "Directories Only", opts.dirs_only),
            
            Separator(" FILTERS "),
            filter_item(
                "edit_layers",
                "Filter Layers",
                opts.layers is None,
                len(opts.layers or []),
            ),
        ]

        # Conditionally add Macro Filter
        if has_macros:
            choices.append(
                filter_item(
                    "edit_macros",
                    "Filter Macros",
                    opts.macro_contexts is None,
                    len(opts.macro_contexts or []),
                )
            )

        choices.append(
            filter_item(
                "edit_contexts",
                "Filter Contexts",
                opts.contexts is None,
                len(opts.contexts or []),
            )
        )
            
        choices.extend([
            Separator(),
            Choice(value="check_config", name="    Check Configuration"),
            Separator(),
            Choice(value="run", name=">>> EXECUTE SCAN <<<"),
            Choice(value="cancel", name="    Exit / Cancel"),
        ])
        
        return choices

    def _edit_depth_subscreen(self) -> None:
        """Popup to set integer depth."""
        result = ask_text(
            message="Enter Max Import Depth (0-5)",
            default=str(self.options.import_depth),
            theme=SCANNER_THEME,
        )
        if result and result.isdigit():
            val = int(result)
            self.options.import_depth = min(val, 10)

    def _edit_layers_subscreen(self) -> None:
        current_set = (
            set(self.options.layers)
            if self.options.layers
            else set(self.available_layers)
        )

        choices = [
            Choice(value=layer, name=layer.title(), enabled=(layer in current_set))
            for layer in self.available_layers
        ]

        console.clear()
        console.print(
            Panel(
                "[bold white]Select Architectural Layers[/]",
                subtitle="[dim]Space to Toggle • Enter to Confirm[/]",
                border_style=SCANNER_THEME.primary_color,
                expand=True,
            )
        )

        result = ask_multiselect(
            message=None, choices=choices, theme=SCANNER_THEME, instruction=""
        )

        if result is not None:
            if len(result) == len(self.available_layers):
                self.options.layers = None
            else:
                self.options.layers = result

    def _edit_macros_subscreen(self) -> None:
        """
        Logic for selecting Macro Contexts.
        Selection here AUTOMATICALLY updates 'contexts' list.
        """
        # Map: "core_system" -> "core" (Folder)
        macro_map = self.config.project.macro_contexts
        
        # We need a special key for "General" (contexts not in any macro folder)
        GENERAL_KEY = "<General>"
        
        console.clear()
        console.print(
            Panel(
                "[bold white]Filter by Macro Contexts[/]\n"
                "[dim]Selecting a Macro will automatically select its Bounded Contexts.[/]",
                subtitle="[dim]Space to Toggle • Enter to Confirm[/]",
                border_style=SCANNER_THEME.primary_color,
                expand=True,
            )
        )

        current_selection = set(self.options.macro_contexts or [])
        
        # Build Choices
        choices = []
        # Add Defined Macros
        for zone, folder in macro_map.items():
            label = f"{zone} (/{folder})"
            choices.append(Choice(value=zone, name=label, enabled=(zone in current_selection)))
        
        # Add General Option
        choices.append(Choice(value=GENERAL_KEY, name="General / Root", enabled=(GENERAL_KEY in current_selection)))

        result = ask_multiselect(
            message=None, choices=choices, theme=SCANNER_THEME, instruction=""
        )

        if result is not None:
            if not result:
                # Empty selection -> Scan All
                self.options.macro_contexts = None
                self.options.contexts = None
            else:
                self.options.macro_contexts = result
                # AUTO-POPULATE CONTEXTS
                self._recalc_contexts_from_macros(result, GENERAL_KEY)

    def _recalc_contexts_from_macros(self, selected_macros: List[str], general_key: str) -> None:
        """
        Helper: Looks at filesystem and populates self.options.contexts based on macro selection.
        """
        root = self.config.project.absolute_source_path
        macro_map = self.config.project.macro_contexts # {zone: folder}
        
        # Invert map for easier lookup: folder -> zone
        folder_to_zone = {v: k for k, v in macro_map.items()}
        
        found_contexts = []

        if not root.exists():
            return

        # Define internal layers to skip (so we don't select 'domain' as a context)
        # Standard symmetric DDD layers + common folders
        ignored_layers = {
            "domain", "app", "ports", "adapters", "composition", 
            "infrastructure", "shared", "tests", "docs"
        }

        # Iterate all top-level directories in src/
        for entry in root.iterdir():
            if not entry.is_dir() or entry.name.startswith((".", "_")):
                continue
            
            # Case A: Entry IS a macro folder (e.g. src/core)
            if entry.name in folder_to_zone:
                zone = folder_to_zone[entry.name]
                if zone in selected_macros:
                    # 1. Add the Macro Orchestrator itself
                    found_contexts.append(entry.name)

                    # 2. Add Sub-Contexts
                    for sub in entry.iterdir():
                        if sub.is_dir() and not sub.name.startswith((".", "_")):
                            # Important: Filter out standard layers
                            if sub.name.lower() not in ignored_layers:
                                found_contexts.append(sub.name)
            
            # Case B: Entry is a Context in General space (e.g. src/shared)
            else:
                if general_key in selected_macros:
                    found_contexts.append(entry.name)

        self.options.contexts = found_contexts

    def _edit_contexts_subscreen(self) -> None:
        source_path = self.config.project.absolute_source_path
        # Returns List[(ContextName, MacroZone|None)]
        available_contexts = self._discover_all_contexts(source_path)

        console.clear()
        console.print(
            Panel(
                "[bold white]Filter Bounded Contexts[/]",
                subtitle="[dim]Type to search • Tab to Select • Enter to Confirm[/]",
                border_style=SCANNER_THEME.primary_color,
                expand=True,
            )
        )

        if not available_contexts:
            result = ask_text(message="Contexts (comma separated)", theme=SCANNER_THEME)
            if result:
                self.options.contexts = [
                    c.strip() for c in result.split(",") if c.strip()
                ]
            return

        current_selection = set(self.options.contexts or [])
        
        # --- SORTING LOGIC ---
        # 1. General Contexts (None) first
        # 2. Then Macro Contexts sorted by Zone Name
        # 3. Within Macro: Orchestrator first (name == folder), then alphabetically
        def sort_key(item):
            ctx_name, macro_zone = item
            if macro_zone is None:
                return (0, "", ctx_name) # Group 0: General
            
            # Check if this is the orchestrator (context name matches the physical folder associated with the zone)
            # We don't have the physical map here easily, but we can assume if ctx_name == macro_folder_name
            # Since we only have zone tag here, let's just push sub-modules after.
            # Usually Orchestrator name (scanner) matches the folder.
            
            return (1, macro_zone, ctx_name)

        available_contexts.sort(key=sort_key)

        # Enhanced Display: [macro: name] context
        choices = []
        for ctx_name, macro_zone in available_contexts:
            if macro_zone:
                # Highlight if it's the orchestrator for that zone (heuristic: usually same name or 'shared')
                # But here we just print them.
                label = f"[macro: {macro_zone}] {ctx_name}"
            else:
                label = ctx_name

            choices.append(Choice(
                value=ctx_name, 
                name=label, 
                enabled=(ctx_name in current_selection)
            ))

        result = ask_select(
            message=None,
            choices=choices,
            use_fuzzy=True,
            multiselect=True,
            theme=SCANNER_THEME,
            instruction="",
        )

        if result is not None:
            self.options.contexts = result if result else None

    def _discover_all_contexts(self, root: Path) -> List[Tuple[str, Optional[str]]]:
        """
        Recursively finds contexts.
        Returns a list of tuples: (ContextName, MacroZoneName|None).
        """
        results = []
        if not root.exists():
            return []
            
        macro_map = self.config.project.macro_contexts # {zone: folder_name}
        # Invert map for checks: folder -> zone
        folder_to_zone = {v: k for k, v in macro_map.items()}

        # Layers to ignore inside a Macro Context folder
        ignored_layers = {
            "domain", "app", "ports", "adapters", "composition", 
            "infrastructure", "shared", "tests", "docs", "__pycache__"
        }

        for entry in root.iterdir():
            if not entry.is_dir() or entry.name.startswith((".", "_")):
                continue
                
            if entry.name in folder_to_zone:
                # It is a Macro Root (e.g. 'scanner')
                zone_name = folder_to_zone[entry.name]
                
                # 1. Add the Orchestrator (The Macro folder itself acts as a context)
                results.append((entry.name, zone_name))

                # 2. Scan for Sub-Contexts
                for sub in entry.iterdir():
                    if not sub.is_dir() or sub.name.startswith((".", "_")):
                        continue
                    
                    # Filter out standard layers. 
                    # Anything NOT a layer is considered a Sub-Context.
                    if sub.name.lower() not in ignored_layers:
                        results.append((sub.name, zone_name))
            else:
                # General context (root level)
                results.append((entry.name, None))
        
        return results

    def _show_config_subscreen(self) -> None:
        console.print(
            "[dim]Config check skipped to avoid circular imports in snippet.[/]"
        )
        console.print("\n[dim]Press Enter to return...[/]")
        try:
            console.input()
        except KeyboardInterrupt:
            pass