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

    def register_commands(self, app: typer.Typer):
        driving_adapter.register_commands(
            app,
            self.controller,
        )


class ScaffolderProvider(Provider):
    scope = Scope.APP

    # --- Driven Adapters ---
    @provide
    def provide_fs_gateway(self) -> IFileSystemGateway:
        return DiskFileSystemGateway()

    # --- Use Cases ---
    @provide
    def provide_create_config_use_case(
        self, gateway: IFileSystemGateway
    ) -> CreateConfigUseCase:
        return CreateConfigUseCase(fs_gateway=gateway)

    # --- Driving Ports (Controllers) ---
    @provide
    def provide_controller(
        self, config_uc: CreateConfigUseCase
    ) -> ScaffolderController:
        return ScaffolderController(create_config_use_case=config_uc)

    # --- Container Facade ---
    @provide
    def provide_container(
        self,
        controller: ScaffolderController,
    ) -> ScaffolderContainer:
        return ScaffolderContainer(
            controller=controller,
        )
