from pathlib import Path

import typer

from dddguard.shared.adapters.driving import tui

from ...ports.driving.facade import InitProjectResponseSchema, ScaffolderFacade


def register_commands(
    app: typer.Typer,
    facade: ScaffolderFacade,
):
    """
    Registers the 'init' command to the main application.
    """

    @app.command(name="init")
    def init(path: Path = typer.Argument(".", help="Project root path")):
        """
        🚀 Initialize DDDGuard configuration.
        Creates docs/dddguard/config.yaml.
        """
        target_root = path.resolve()

        tui.console.print(f"[dim]Initializing project at: {target_root}...[/dim]")

        # Adapter calls Port
        response: InitProjectResponseSchema = facade.init_project(target_root)

        # Adapter handles Presentation logic based on Schema
        if response.success:
            tui.success(response.message, {"Config": f"[bold white]{response.config_path}[/]"})
        # Handle failure scenarios (Existed or Error)
        elif "already exists" in response.message:
            tui.warning(response.message, {"Path": str(response.config_path)})
        else:
            tui.error(
                response.message,
                {"Details": str(response.error_details)} if response.error_details else None,
            )
            raise typer.Exit(1)
