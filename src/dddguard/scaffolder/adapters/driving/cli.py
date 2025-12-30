import typer
from pathlib import Path
from rich.console import Console

from ...ports.driving import ScaffolderController, InitProjectResponseSchema

console = Console()


def register_commands(
    app: typer.Typer,
    controller: ScaffolderController,
):
    """
    Registers the 'init' command to the main application.
    Injects the Controller (Port), NOT the UseCase.
    """

    @app.command(name="init")
    def init(path: Path = typer.Argument(".", help="Project root path")):
        """
        🚀 Initialize DDDGuard configuration.
        Creates docs/dddguard/config.yaml.
        """
        target_root = path.resolve()

        console.print(f"[dim]Initializing project at: {target_root}...[/dim]")

        # Adapter calls Port
        response: InitProjectResponseSchema = controller.init_project(target_root)

        # Adapter handles Presentation logic based on Schema
        if response.success:
            console.print(f"[green]✅ {response.message}[/green]")
            console.print(f"   Config: [bold white]{response.config_path}[/]")
        else:
            # Handle failure scenarios (Existed or Error)
            if "already exists" in response.message:
                console.print(f"[yellow]⚠️  {response.message}[/yellow]")
                console.print(f"   Path: {response.config_path}")
            else:
                console.print(f"[bold red]❌ {response.message}[/bold red]")
                if response.error_details:
                    console.print(f"   Details: {response.error_details}")
                raise typer.Exit(1)
