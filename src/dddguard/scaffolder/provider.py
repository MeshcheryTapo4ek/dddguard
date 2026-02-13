from dataclasses import dataclass

import typer
from dishka import Provider, Scope, provide

from .adapters.driven.disk_file_system_gateway import DiskFileSystemGateway
from .adapters.driving import cli as driving_adapter

# Dependencies for wiring
from .app import (
    CreateConfigUseCase,
    IFileSystemGateway,
)
from .ports.driving.facade import ScaffolderFacade


@dataclass(frozen=True, kw_only=True, slots=True)
class ScaffolderContainer:
    """
    Facade Container for Scaffolder Context.
    Exposes the facade via the CLI adapter.
    """

    facade: ScaffolderFacade

    def register_commands(self, app: typer.Typer) -> None:
        """
        Delegates command registration to the driving adapter logic.
        """
        driving_adapter.register_commands(app, self.facade)


class ScaffolderProvider(Provider):
    """
    DI Provider for the Scaffolder Context.
    Wires file system access and configuration logic.
    """

    scope = Scope.APP
    fs_gateway = provide(DiskFileSystemGateway, provides=IFileSystemGateway)
    create_config_use_case = provide(CreateConfigUseCase)
    facade = provide(ScaffolderFacade)
    container = provide(ScaffolderContainer)
