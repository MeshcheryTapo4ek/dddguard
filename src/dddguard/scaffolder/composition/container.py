from dataclasses import dataclass
import typer
from dishka import Provider, Scope, provide

# Dependencies for wiring
from ..app import (
    CreateConfigUseCase,
    IFileSystemGateway,
)
from ..ports.driving import ScaffolderController
from ..adapters.driven import DiskFileSystemGateway
from ..adapters.driving import cli as driving_adapter


@dataclass(frozen=True, kw_only=True, slots=True)
class ScaffolderContainer:
    """
    Facade for Scaffolder Context.
    Exposes the Controller via the CLI adapter.
    """
    controller: ScaffolderController

    def register_commands(self, app: typer.Typer) -> None:
        """
        Delegates command registration to the driving adapter logic.
        """
        driving_adapter.register_commands(app, self.controller)


class ScaffolderProvider(Provider):
    """
    DI Provider for the Scaffolder Context.
    Wires file system access and configuration logic.
    """
    
    scope = Scope.APP

    # Driven Adapter: Bind Implementation to Interface
    fs_gateway = provide(DiskFileSystemGateway, provides=IFileSystemGateway)

    # Application Layer (Use Case)
    create_config_use_case = provide(CreateConfigUseCase)

    # Driving Port (Controller)
    controller = provide(ScaffolderController)

    # Context Root
    container = provide(ScaffolderContainer)