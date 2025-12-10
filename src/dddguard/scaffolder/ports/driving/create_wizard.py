from typing import List, Any, Optional, Tuple, Union
from pathlib import Path
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.table import Table
from rich.tree import Tree
from rich import box

from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator

from dddguard.shared.ports.driving.ui import (
    SCAFFOLDER_THEME, 
    ask_select
)

console = Console()

class CreateComponentWizard:
    """
    Interactive Wizard for Scaffolding DDD Components.
    Theme: Blue (Engineering/Construction).
    """
    def __init__(self, config, list_use_case):
        self.config = config
        self.list_use_case = list_use_case
        self.theme_color = SCAFFOLDER_THEME.primary_color
        
        # Requirement: Save to 'templates' folder at the same level as 'src'
        # Usually project_root is the parent of src.
        self.templates_path = self.config.project.project_root / "templates"

    def run(self) -> Union[Tuple[str, str, Path], str, None]:
        """
        Main Loop.
        Returns: 
            - (category, template_name, target_path) for creation
            - "INIT_CONFIG" signal
            - None for cancel
        """
        while True:
            console.clear()
            self._render_dashboard()
            
            choices = self._build_menu()
            
            action = ask_select(
                message=None, 
                choices=choices, 
                theme=SCAFFOLDER_THEME,
                instruction=""
            )
            
            if action == "cancel" or action is None:
                return None
            
            if action == "browse":
                self._show_registry()
                continue
                
            if action == "init_config":
                return "INIT_CONFIG"

            if action == "create":
                # Start the selection flow
                result = self._run_generation_flow()
                if result:
                    # Return category, template, and the FIXED templates path
                    return result[0], result[1], self.templates_path
                # If flow returned None (user went back), loop again

    def _build_menu(self) -> List[Any]:
        choices = [Separator(" ACTIONS ")]
        
        # Option 1: Browse is always available
        choices.append(Choice(value="browse", name="   📚 Browse Template Registry"))
        
        # Option 2: Action depends on Config existence
        if self.config.project.has_config_file:
            choices.append(Choice(value="create", name="   🧩 Generate New Component"))
        else:
            # Highlighted option to suggest fixing the missing config
            choices.append(Choice(value="init_config", name="   ⚙️  Initialize Configuration (Recommended)"))
            # We still allow creation in ad-hoc mode, but maybe warn? 
            # For now, let's keep it strict or allow ad-hoc. 
            # Let's allow ad-hoc creation but below the config option.
            choices.append(Choice(value="create", name="   ⚡ Ad-Hoc Generation (No Config)"))

        choices.append(Separator())
        choices.append(Choice(value="cancel", name="   Exit"))
        return choices

    def _render_dashboard(self):
        color = self.theme_color
        has_config = self.config.project.has_config_file
        
        # --- Header ---
        project_name = self.config.project.project_root.name
        
        header_text = Text()
        header_text.append(f"Project: {project_name}\n", style="bold white")
        
        if has_config:
            header_text.append("Config:  ✅ Loaded", style="bold green")
        else:
            header_text.append("Config:  ⚠️  Missing", style="bold yellow")

        # --- Details Grid ---
        grid = Table.grid(padding=(0, 2))
        grid.add_column(style="dim", justify="right", min_width=15)
        grid.add_column(style="bold white")
        
        # Path logic display
        rel_path = self._get_relative_path(self.templates_path)
        
        grid.add_row("Root:", str(self.config.project.project_root))
        grid.add_row("Target Dir:", f"[{color}]{rel_path}[/]")
        
        content = Group(
            Align.center(header_text),
            Text(" "), # Spacer
            Align.center(grid)
        )

        panel = Panel(
            content,
            title=f"[bold {color}] COMPONENT SCAFFOLDER [/]",
            subtitle="[dim]Generates boilerplate code into /templates[/]",
            border_style=color,
            padding=(1, 2),
            box=box.ROUNDED,
            expand=True
        )
        console.print(panel)

    def _run_generation_flow(self) -> Optional[Tuple[str, str]]:
        """
        Sub-flow: Select Category -> Select Template.
        """
        # 1. Fetch Data
        categories_map, grouped_templates = self.list_use_case.execute()
        
        # 2. Select Category
        cat_choices = []
        for cat_id in sorted(grouped_templates.keys()):
            cat_meta = categories_map.get(cat_id)
            desc = f" ({cat_meta.title})" if cat_meta else ""
            cat_choices.append(Choice(value=cat_id, name=f"📂 {cat_id}{desc}"))
            
        cat_choices.append(Separator())
        cat_choices.append(Choice(value="back", name="🔙 .. (Back)"))

        category = ask_select(
            message="Select Category", 
            choices=cat_choices, 
            theme=SCAFFOLDER_THEME
        )
        
        if not category or category == "back":
            return None

        # 3. Select Template
        tmpl_choices = []
        for tmpl in grouped_templates[category]:
            desc = f" - {tmpl.description}" if tmpl.description else ""
            tmpl_choices.append(Choice(value=tmpl.id, name=f"📄 {tmpl.id}{desc}"))
            
        tmpl_choices.append(Separator())
        tmpl_choices.append(Choice(value="back", name="🔙 .. (Back)"))

        template = ask_select(
            message=f"Select {category} Template", 
            choices=tmpl_choices, 
            theme=SCAFFOLDER_THEME
        )

        if not template or template == "back":
            return None
            
        return category, template

    def _show_registry(self):
        """Displays the Tree of available templates."""
        categories_map, grouped_templates = self.list_use_case.execute()
        
        console.clear()
        console.print(Panel(
            "[bold white]Template Registry[/]", 
            style=f"{self.theme_color}", 
            box=box.HEAVY_HEAD
        ))
        
        tree = Tree(f"📦 [bold {self.theme_color}]Available Components[/]")
        
        for cat_id in sorted(grouped_templates.keys()):
            cat_def = categories_map.get(cat_id)
            title = f"[bold cyan]📂 {cat_def.title if cat_def else cat_id}[/]"
            cat_node = tree.add(title)
            
            for tmpl in grouped_templates[cat_id]:
                label = f"[bold white]{tmpl.id}[/]"
                if tmpl.description:
                    label += f" [dim]- {tmpl.description}[/]"
                cat_node.add(label)
                
        console.print(tree)
        console.print("\n[dim]Press Enter to return...[/]")
        console.input()

    def _get_relative_path(self, path: Path) -> str:
        try:
            # Try to show relative to cwd for readability
            return f"./{path.relative_to(Path.cwd())}"
        except ValueError:
            return str(path)