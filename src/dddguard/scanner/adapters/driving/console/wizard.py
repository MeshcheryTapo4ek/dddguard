from typing import Any

from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from rich.markup import escape

from dddguard.shared.adapters.driving import (
    SCANNER_THEME,
    tui,
)
from dddguard.shared.domain import LayerEnum

from ....ports.driving import ScannerFacade
from .scan_options import ScanOptions


class ScanSettingsWizard:
    def __init__(self, options: ScanOptions, facade: ScannerFacade):
        self.options = options
        self.facade = facade
        self.config = facade.config

        self.available_layers = [
            layer for layer in LayerEnum if layer not in (LayerEnum.GLOBAL, LayerEnum.UNDEFINED)
        ]

        # --- AUTO-DISCOVERY ON STARTUP ---
        self._all_contexts: list[tuple[str, str | None]] = []
        self._all_macros: set[str] = set()
        self._run_initial_discovery()

    def _run_initial_discovery(self) -> None:
        try:
            with tui.spinner("Discovering Project Structure...", spinner_type="dots"):
                # Call Facade -> DiscoverContextsUseCase
                # Returns ContextListSchema
                schema = self.facade.discover_contexts(target_path=self.options.target_path)

                # Unpack Schema
                self._all_contexts = [(c.context_name, c.macro_zone) for c in schema.contexts]
                self._all_macros = {c.macro_zone for c in schema.contexts if c.macro_zone}
        except Exception as e:
            safe_error = escape(str(e))
            tui.console.print(f"[bold red]Discovery Failed:[/bold red] {safe_error}")
            tui.console.print(
                "[dim yellow]Context/macro filters unavailable. Layer filters still work.[/]"
            )

    def run(self) -> bool:
        last_pointer_value = "run"
        tui.set_theme(SCANNER_THEME)  # Set local theme

        while True:
            tui.clear()
            self._render_dashboard()

            choices = self._build_main_menu_choices()

            action = tui.select(
                message=None,
                choices=choices,
                default=last_pointer_value,
                instruction="",
            )

            if action is None or action == "cancel":
                tui.clear()
                return False

            if action == "run":
                return True

            self._handle_action(action)
            last_pointer_value = action

    def _handle_action(self, action: str) -> None:
        opts = self.options

        if action == "toggle_all":
            opts.scan_all = not opts.scan_all
        elif action == "toggle_file_tree_only":
            opts.file_tree_only = not opts.file_tree_only

        # [CHANGED] Removed toggle_shared/toggle_root handlers

        elif action == "toggle_assets":
            opts.include_assets = not opts.include_assets

        elif action == "edit_depth":
            self._edit_depth_subscreen()
        elif action == "edit_layers":
            self._edit_layers_subscreen()
        elif action == "edit_macros":
            self._edit_macros_subscreen()
        elif action == "edit_contexts":
            self._edit_contexts_subscreen()
        elif action == "check_config":
            self._show_config_subscreen()

    def _render_dashboard(self) -> None:
        opts = self.options
        color = SCANNER_THEME.primary_color

        # 1. Prepare Left Data (Settings)
        depth_val = f"{opts.import_depth} levels" if opts.import_depth > 0 else "None (Strict)"
        depth_style = "bold yellow" if opts.import_depth > 0 else "dim"

        content_val = "MASKED (<Some Content>)" if opts.file_tree_only else "INCLUDED (Full Code)"
        content_style = "dim red" if opts.file_tree_only else "green"

        def toggle_style(val: bool) -> str:
            return "[green]ON[/]" if val else "[dim red]OFF[/]"

        settings_data = {
            "Mode": "All Files" if opts.scan_all else "Python Only",
            "Imp. Depth": f"[{depth_style}]{depth_val}[/]",
            "Content": f"[{content_style}]{content_val}[/]",
            # [CHANGED] Removed Shared/Root from dashboard display
            "Assets": toggle_style(opts.include_assets),
        }

        # 2. Prepare Right Data (Filters)
        l_count = f"{len(opts.layers)}/{len(self.available_layers)}" if opts.layers else "ALL"

        total_macros = len(self._all_macros)
        if opts.macro_contexts:
            m_count = f"{len(opts.macro_contexts)}/{total_macros}"
        else:
            m_count = "ALL"

        c_status = "ALL" if opts.contexts is None else f"{len(opts.contexts)} selected"

        filter_data = {"Layers": l_count, "Macros": m_count, "Contexts": c_status}

        # 3. Determine Title Path
        source_root = self.config.project.absolute_source_path
        if opts.target_path and source_root and opts.target_path.resolve() == source_root.resolve():
            path_display = f"Project Source ({self.config.project.source_dir})"
        else:
            path_display = str(opts.target_path) if opts.target_path else "N/A"

        # 4. Render using TUI
        tui.dashboard(
            title="Scanner Configuration",
            subtitle="Arrows to navigate • Enter to toggle",
            data=[settings_data, filter_data],  # Two Columns
        )

        tui.console.print(f"Target: [bold {color}]{path_display}[/]", justify="center")

    def _build_main_menu_choices(self) -> list[Any]:
        opts = self.options

        def item(key, label, is_active):
            status = "[ON] " if is_active else "[OFF]"
            return Choice(value=key, name=f"{label:<25} {status}")

        def filter_item(key, label, is_all):
            val = "[ALL]" if is_all else "[FILTERED]"
            return Choice(value=key, name=f"{label:<25} {val}")

        def value_item(key, label, value):
            return Choice(value=key, name=f"{label:<25} [{value}]")

        return [
            Separator(" STRATEGY "),
            item("toggle_all", "Scan All Files", opts.scan_all),
            item("toggle_file_tree_only", "Mask File Content", opts.file_tree_only),
            value_item("edit_depth", "Import Depth", opts.import_depth),
            item("toggle_assets", "Include Assets/Res", opts.include_assets),
            Separator(" FILTERS "),
            # [CHANGED] Removed individual toggles for Shared/Root
            filter_item(
                "edit_contexts",
                "Filter Contexts (Root/Shared incl.)",
                opts.contexts is None,
            ),
            filter_item("edit_layers", "Filter Layers", opts.layers is None),
            filter_item("edit_macros", "Filter Macros", opts.macro_contexts is None),
            Separator(),
            Choice(value="check_config", name="      Check Configuration"),
            Separator(),
            Choice(value="run", name=">>> EXECUTE SCAN <<<"),
            Choice(value="cancel", name="      Exit / Cancel"),
        ]

    def _edit_depth_subscreen(self) -> None:
        result = tui.text(
            message="Enter Max Import Depth (0-5)",
            default=str(self.options.import_depth),
        )
        if result and result.isdigit():
            self.options.import_depth = min(int(result), 10)

    def _edit_layers_subscreen(self) -> None:
        current = (
            set(self.options.layers)
            if self.options.layers
            else {layer.value for layer in self.available_layers}
        )

        choices = [
            Choice(
                value=layer.value,
                name=layer.value.title(),
                enabled=(layer.value in current),
            )
            for layer in self.available_layers
        ]

        tui.clear()
        tui.console.print("[bold white]Select Layers[/]")
        result = tui.multiselect(message=None, choices=choices)

        if result is not None:
            self.options.layers = None if len(result) == len(self.available_layers) else result

    def _edit_macros_subscreen(self) -> None:
        if not self._all_macros:
            result = tui.text(
                message="No macro zones. Enter manually (comma-separated)",
            )
            if result:
                self.options.macro_contexts = [m.strip() for m in result.split(",") if m.strip()]
            return

        tui.clear()
        tui.console.print("[bold white]Filter by Macro Contexts[/]")

        sorted_macros = sorted(list(self._all_macros))
        current_selection = set(self.options.macro_contexts or [])

        choices = []
        for m in sorted_macros:
            choices.append(Choice(value=m, name=m, enabled=(m in current_selection)))

        result = tui.multiselect(message=None, choices=choices)

        if result is not None:
            if not result:
                self.options.macro_contexts = None
            else:
                self.options.macro_contexts = result
                self._recalc_contexts_from_macros(result)

    def _recalc_contexts_from_macros(self, selected_macros: list[str]) -> None:
        found = []
        for name, macro in self._all_contexts:
            if macro and macro in selected_macros:
                found.append(name)
        self.options.contexts = found

    def _edit_contexts_subscreen(self) -> None:
        tui.clear()
        tui.console.print("[bold white]Filter Bounded Contexts[/]")

        if not self._all_contexts:
            tui.warning(
                "No Discovery Data",
                "No contexts found. Try scanning from project root.",
            )
            tui.pause()
            return

        current_ctx_list = self.options.contexts or []
        choices = []

        # Sort: Root -> Shared -> Others
        def sort_key(x):
            if x[0] == "root":
                return "0"
            if x[0] == "shared":
                return "1"
            return f"2_{x[1] or ''}_{x[0]}"

        sorted_ctx = sorted(self._all_contexts, key=sort_key)

        for name, macro in sorted_ctx:
            # Plain text labels for InquirerPy (doesn't support Rich markup)
            if name == "root":
                label = "ROOT"
            elif name == "shared":
                label = "SHARED"
            else:
                label = f"[{macro}] {name}" if macro else name

            is_enabled = (name in current_ctx_list) if self.options.contexts is not None else True
            choices.append(Choice(value=name, name=label, enabled=is_enabled))

        result = tui.multiselect(message=None, choices=choices, use_fuzzy=True)

        if result is not None:
            if len(result) == 0 or len(result) == len(self._all_contexts):
                self.options.contexts = None
            else:
                self.options.contexts = result

    def _show_config_subscreen(self) -> None:
        config = self.config

        config_data = {
            "Project Root": str(config.project.project_root),
            "Source Dir": config.project.source_dir,
            "Tests Dir": config.project.tests_dir,
            "Docs Dir": config.project.docs_dir,
            "Exclude Dirs": ", ".join(sorted(config.scanner.exclude_dirs)[:5])
            + ("..." if len(config.scanner.exclude_dirs) > 5 else ""),
            "Ignore Files": ", ".join(sorted(config.scanner.ignore_files)[:5])
            + ("..." if len(config.scanner.ignore_files) > 5 else ""),
        }

        tui.clear()
        tui.dashboard(
            title="Current Configuration",
            subtitle="Loaded from config.yaml",
            data=config_data,
        )
        tui.pause()
