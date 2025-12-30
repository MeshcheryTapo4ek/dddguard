from typing import List, Any
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
            # Simple check, in production might need robust path comparison
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

        def item(key, label, is_active):
            status = "[ON] " if is_active else "[OFF]"
            return Choice(value=key, name=f"{label:<22} {status}")

        def filter_item(key, label, is_all, count):
            val = "[ALL]" if is_all else f"[{count}]"
            return Choice(value=key, name=f"{label:<22} {val}")
        
        # Helper for value display items
        def value_item(key, label, value):
            return Choice(value=key, name=f"{label:<22} [{value}]")

        return [
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
            filter_item(
                "edit_contexts",
                "Filter Contexts",
                opts.contexts is None,
                len(opts.contexts or []),
            ),
            
            Separator(),
            Choice(value="check_config", name="    Check Configuration"),
            Separator(),
            Choice(value="run", name=">>> EXECUTE SCAN <<<"),
            Choice(value="cancel", name="    Exit / Cancel"),
        ]

    def _edit_depth_subscreen(self) -> None:
        """Popup to set integer depth."""
        result = ask_text(
            message="Enter Max Import Depth (0-5)",
            default=str(self.options.import_depth),
            theme=SCANNER_THEME,
        )
        if result and result.isdigit():
            val = int(result)
            # Cap at reasonable limit to prevent explosions
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

    def _edit_contexts_subscreen(self) -> None:
        source_path = self.config.project.absolute_source_path
        available_contexts = []
        if source_path.exists():
            available_contexts = [
                d.name
                for d in source_path.iterdir()
                if d.is_dir() and not d.name.startswith(("_", "."))
            ]

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
        choices = [
            Choice(value=ctx, name=ctx, enabled=(ctx in current_selection))
            for ctx in available_contexts
        ]

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

    def _show_config_subscreen(self) -> None:
        # Avoid circular import or duplication; basic rendering or a placeholder
        # In a real app, render_config_info would be imported from shared adapters
        console.print(
            "[dim]Config check skipped to avoid circular imports in snippet.[/]"
        )
        console.print("\n[dim]Press Enter to return...[/]")
        try:
            console.input()
        except KeyboardInterrupt:
            pass