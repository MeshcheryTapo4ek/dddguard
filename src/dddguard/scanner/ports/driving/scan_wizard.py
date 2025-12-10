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

from dddguard.shared import ContextLayerEnum, ConfigVo
from dddguard.shared.ports.driving.ui import (
    SCANNER_THEME, 
    ask_select, 
    ask_multiselect,
    ask_text,
    render_config_info # <--- Added Import
)
from .scan_options import ScanOptions

console = Console()

class ScanSettingsWizard:
    def __init__(self, options: ScanOptions, config: ConfigVo):
        self.options = options
        self.config = config
        self.available_layers = [
            l.value for l in ContextLayerEnum 
            if l != ContextLayerEnum.OTHER
        ]

    def run(self) -> bool:
        """Main Event Loop."""
        # Default cursor position set to "run"
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
                instruction="" 
            )
            
            # Ctrl+C returns None
            if action is None or action == "cancel":
                console.clear() 
                return False
            
            if action == "run":
                return True
            
            self._handle_action(action)
            
            # Save the value for the next iteration to keep cursor position
            last_pointer_value = action

    def _handle_action(self, action: str):
        opts = self.options
        
        if action == "toggle_verbose": opts.verbose = not opts.verbose
        elif action == "toggle_all": opts.scan_all = not opts.scan_all
        elif action == "toggle_dirs": opts.dirs_only = not opts.dirs_only
        elif action == "toggle_root": opts.show_root = not opts.show_root
        elif action == "toggle_shared": opts.show_shared = not opts.show_shared

        elif action == "edit_layers": 
            self._edit_layers_subscreen()
        elif action == "edit_contexts": 
            self._edit_contexts_subscreen()
        
        elif action == "check_config": # <--- Handle new action
            self._show_config_subscreen()

    def _render_dashboard(self):
        opts = self.options
        color = SCANNER_THEME.primary_color
        
        # --- 1. Top Section: Target Path ---
        path_str = str(opts.target_path)
        is_project_root = False
        source_dir_display = "Unknown"
        
        if self.config.project:
             is_project_root = (opts.target_path == self.config.project.absolute_source_path)
             source_dir_display = str(self.config.project.source_dir)

        path_text = Text()
        path_text.append("Target: ", style="dim")
        if is_project_root:
            path_text.append("Project Source ", style=f"bold {color}")
            path_text.append(f"({source_dir_display})", style="white")
        else:
            path_text.append(path_str, style=f"bold {color}")

        # --- 2. Grid Section: Settings & Filters ---
        
        # Left Column: Flags
        settings_table = Table.grid(padding=(0, 2))
        settings_table.add_column(style="dim", justify="right", min_width=10)
        settings_table.add_column(style="bold white")
        
        settings_table.add_row("Mode:", "All Files" if opts.scan_all else "Python Only")
        settings_table.add_row("Type:", "Directories Only" if opts.dirs_only else "Full Tree")
        settings_table.add_row("Verbose:", "[green]ON[/]" if opts.verbose else "[dim]OFF[/]")

        # Right Column: Scope & Filters
        filter_table = Table.grid(padding=(0, 2))
        filter_table.add_column(style="dim", justify="right", min_width=10)
        filter_table.add_column(style=f"bold {color}")
        
        l_count = len(opts.layers) if opts.layers else "ALL"
        c_count = len(opts.contexts) if opts.contexts else "ALL"
        filter_table.add_row("Layers:", f"{l_count}")
        filter_table.add_row("Contexts:", f"{c_count}")
        
        scope_str = []
        if opts.show_root: scope_str.append("Root")
        if opts.show_shared: scope_str.append("Shared")
        if not scope_str: scope_str.append("Contexts Only")
        filter_table.add_row("Scope:", ", ".join(scope_str))

        # Combine columns
        grid = Table(box=None, expand=True, padding=0, show_header=False)
        grid.add_column(ratio=5) 
        grid.add_column(ratio=5) 
        grid.add_row(settings_table, filter_table)

        # --- 3. Assemble Panel ---
        content = Group(
            Align.center(path_text),
            Rule(style=f"dim {color}"),
            grid
        )

        panel = Panel(
            content,
            title=f"[bold {color}]Scanner Configuration[/]",
            subtitle="[dim]Arrows to navigate • Enter to toggle[/]",
            subtitle_align="right", 
            border_style=color,
            padding=(1, 2),
            expand=True 
        )
        console.print(panel)

    def _build_main_menu_choices(self) -> List[Any]:
        opts = self.options
        
        # Helper to align text nicely without emojis
        def item(key, label, is_active):
            status = "[ON] " if is_active else "[OFF]"
            # Pad label for alignment
            return Choice(value=key, name=f"{label:<20} {status}")
        
        def filter_item(key, label, is_all, count):
            val = "[ALL]" if is_all else f"[{count}]"
            return Choice(value=key, name=f"{label:<20} {val}")

        return [
            Separator(" FLAGS "),
            item("toggle_verbose", "Verbose Mode", opts.verbose),
            item("toggle_dirs", "Directories Only", opts.dirs_only),
            item("toggle_all", "Scan All Files", opts.scan_all),
            
            Separator(" SCOPE "),
            item("toggle_root", "Include Root", opts.show_root),
            item("toggle_shared", "Include Shared", opts.show_shared),
            
            Separator(" FILTERS "),
            filter_item("edit_layers", "Filter Layers", opts.layers is None, len(opts.layers or [])),
            filter_item("edit_contexts", "Filter Contexts", opts.contexts is None, len(opts.contexts or [])),
            
            Separator(),
            Choice(value="check_config", name="    Check Configuration"), # <--- New Option
            Separator(),
            Choice(value="run", name=">>> EXECUTE SCAN <<<"),
            Choice(value="cancel", name="    Exit / Cancel"),
        ]

    def _edit_layers_subscreen(self):
        current_set = set(self.options.layers) if self.options.layers else set(self.available_layers)
        
        choices = [
            Choice(value=layer, name=layer.replace("_", " ").title(), enabled=(layer in current_set))
            for layer in self.available_layers
        ]

        console.clear()
        console.print(Panel(
            "[bold white]Select Architectural Layers[/]", 
            subtitle="[dim]Space to Toggle • Enter to Confirm[/]",
            border_style=SCANNER_THEME.primary_color,
            expand=True
        ))
        
        result = ask_multiselect(
            message=None,
            choices=choices,
            theme=SCANNER_THEME,
            instruction=""
        )
        
        if result is not None:
            if len(result) == len(self.available_layers):
                self.options.layers = None
            else:
                self.options.layers = result

    def _edit_contexts_subscreen(self):
        source_path = self.config.project.absolute_source_path
        
        available_contexts = []
        if source_path.exists():
            available_contexts = [
                d.name for d in source_path.iterdir() 
                if d.is_dir() and not d.name.startswith(("_", "."))
            ]
        
        console.clear()
        console.print(Panel(
            "[bold white]Filter Bounded Contexts[/]",
            subtitle="[dim]Type to search • Tab to Select • Enter to Confirm[/]", 
            border_style=SCANNER_THEME.primary_color,
            expand=True
        ))

        if not available_contexts:
            result = ask_text(message="Contexts (comma separated)", theme=SCANNER_THEME)
            if result: 
                self.options.contexts = [c.strip() for c in result.split(",") if c.strip()]
            return

        current_selection = set(self.options.contexts or [])
        
        choices = []
        
        for ctx in available_contexts:
            is_selected = ctx in current_selection
            choices.append(Choice(value=ctx, name=ctx, enabled=is_selected))

        result = ask_select(
            message=None,
            choices=choices,
            use_fuzzy=True,
            multiselect=True,
            theme=SCANNER_THEME,
            instruction="" 
        )
        
        if result is not None:
            self.options.contexts = result if result else None

    def _show_config_subscreen(self):
        """Displays the static configuration info and waits."""
        console.clear()
        
        if self.config.project.has_config_file:
            render_config_info(self.config, theme=SCANNER_THEME)
        else:
             console.print(Panel(
                "[bold yellow]Running in Ad-hoc mode (No config file found)[/]",
                border_style="yellow",
                expand=False
             ))

        console.print("\n[dim]Press Enter or Ctrl+C to return...[/]")
        try:
            console.input()
        except KeyboardInterrupt:
            pass # Just return to the loop