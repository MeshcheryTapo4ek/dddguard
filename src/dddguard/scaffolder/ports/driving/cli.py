import typer
import time
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table
from rich.tree import Tree
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.align import Align

# --- INFRASTRUCTURE IMPORTS ---
from dddguard.shared.adapters.driven import YamlConfigLoader 
from dddguard.shared.ports.driving.ui import (
    safe_execution
)

# --- APP LAYER ---
from ...app import (
    InitProjectUseCase, 
    CreateConfigUseCase, 
    CreateComponentUseCase,
    ListTemplatesUseCase,
    ScaffolderAppError
)

# --- ADAPTERS & WIZARD ---
from .create_wizard import CreateComponentWizard

console = Console()

def register_commands(
    app: typer.Typer, 
    init_use_case: InitProjectUseCase,
    config_use_case: CreateConfigUseCase,
    create_component_use_case: CreateComponentUseCase,
    list_templates_use_case: ListTemplatesUseCase
):

    @app.command(name="create")
    def create(
        category: str = typer.Argument(None, help="Template Category"),
        name: str = typer.Argument(None, help="Template Name/ID"),
    ):
        """
        🧩 Interactive Component Generator.
        """
        run_create_wizard(
            create_component_use_case, 
            list_templates_use_case,
            config_use_case, 
            category, 
            name
        )

    @app.command(name="init")
    def init(path: Path = typer.Argument(".", help="Project path")):
        """🚀 Initialize project structure."""
        
        target_path = path.resolve()
        
        config_check_path = target_path / "docs" / "dddguard" / "config.yaml"
        
        if config_check_path.exists():
            console.print(f"[yellow]⚠️  Project already initialized. File {config_check_path} already exists.[/yellow]")
            raise typer.Exit()

        project_name = target_path.name

        try:
            init_use_case.execute(target_path, project_name=project_name)
            
            console.print(f"[green]✅ Project successfully created at:[/green] {target_path}")

        except Exception as e:
            console.print(f"[bold red]❌ Failed:[/bold red] {e}")
            raise typer.Exit(1)


# --- PUBLIC REUSABLE FLOWS (Exposed to Root CLI) ---
def run_create_wizard(
    create_uc: CreateComponentUseCase,
    list_uc: ListTemplatesUseCase,
    config_uc: Optional[CreateConfigUseCase] = None, 
    category: Optional[str] = None, 
    template_name: Optional[str] = None
):
    """
    Main entry point for component creation logic.
    """
    # 1. Load Configuration
    config = YamlConfigLoader().load()
    
    # 2. Init Wizard
    wizard = CreateComponentWizard(config, list_uc)

    # 3. Determine Mode
    
    # A. Direct Mode (CLI Args provided)
    if category and template_name:
        # Save to templates folder by default in direct mode too
        target = config.project.project_root / "templates"
        _execute_creation(create_uc, target, category, template_name)
        return

    # B. Interactive Mode (Wizard)
    result = wizard.run()
    
    if result == "INIT_CONFIG":
        if config_uc:
            run_init_config_routine(config_uc)
        else:
            console.print("[red]Config UseCase not available in this context.[/]")
        return

    # If result is a tuple (category, template, path)
    if isinstance(result, tuple):
        cat, tmpl, path = result
        _execute_creation(create_uc, path, cat, tmpl)


# --- PRIVATE HELPERS ---

def _execute_creation(use_case, target_root, category, name):
    """
    Helper to run the use case and print result with a beautiful Tree view.
    """
    
    # Ensure target exists
    if not target_root.exists():
        target_root.mkdir(parents=True, exist_ok=True)

    console.print()
    with safe_execution(status_msg=f"Scaffolding {category}/{name}..."):
            use_case.execute(
                target_root=target_root,
                category=category,
                template_name=name
            )
    # --- Render Beautiful Success Panel with Tree ---
    _render_scaffold_success(target_root, name)

def _render_scaffold_success(target_path: Path, template_name: str):
    """
    Renders a blueprint-style success panel showing the generated file structure.
    """
    # 1. Build the Tree
    tree = Tree(f"📂 [bold blue]{target_path.name}[/]")
    _build_file_tree(target_path, tree)
    
    # 2. Build the Info Grid
    grid = Table.grid(padding=(0, 2))
    grid.add_column(style="dim", justify="right")
    grid.add_column(style="bold white")
    
    grid.add_row("Template:", f"[cyan]{template_name}[/]")
    grid.add_row("Location:", str(target_path))
    grid.add_row("", "") # Spacer
    grid.add_row("Status:", "[bold green]Generated Successfully[/]")

    # 3. Combine in a Panel
    # We use a Group or a Table to stack the info and the tree
    content = Table.grid(expand=True)
    content.add_row(Align.center(grid))
    content.add_row("") # Spacer
    content.add_row(tree)
    content.add_row("")
    content.add_row(Align.center("[dim italic]👉 Move these files to src/ when ready.[/]"))

    panel = Panel(
        content,
        title="[bold blue]🧩 Component Constructed[/]",
        border_style="blue",
        box=box.ROUNDED,
        padding=(1, 2),
        expand=False
    )

    console.print(panel)
    console.print()


def _build_file_tree(path: Path, tree: Tree, limit: int = 10):
    """
    Recursively builds a Rich Tree from the filesystem.
    """
    count = 0
    # Sort: Directories first, then files
    paths = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name))
    
    for p in paths:
        if count >= limit:
            tree.add("... [dim](and more)[/]")
            break
            
        if p.is_dir():
            branch = tree.add(f"📂 [bold blue]{p.name}[/]")
            _build_file_tree(p, branch, limit=5)
        else:
            tree.add(f"📄 {p.name}")
        count += 1


def run_init_config_routine(create_config_uc: CreateConfigUseCase):
    """
    Interactive routine to create the configuration file.
    Used by Root CLI menu even if 'config' command is removed from sub-app.
    """
    project_root = Path.cwd()
    target_config = project_root / "docs" / "dddguard" / "config.yaml"
    
    grid = Table.grid(padding=1)
    grid.add_column(style="dim", justify="right")
    grid.add_column(style="bold white")
    grid.add_row("Location:", str(target_config))
    
    console.print(Panel(grid, title="⚙️  Configuration Setup", border_style="blue"))
    
    if target_config.exists():
        if not Confirm.ask("⚠️  Config exists. Overwrite?", default=False):
            return

    with safe_execution(status_msg="Initializing Config...", error_title="Config Setup Failed"):
        if not target_config.parent.exists():
            target_config.parent.mkdir(parents=True, exist_ok=True)
            
        create_config_uc.execute(target_config)
        console.print(f"[bold green]✅ Config created.[/]")
        time.sleep(0.1)