from dataclasses import dataclass
import typer

from dishka import Provider, Scope, provide

# Interfaces
from ..app import (
    IDetectionGateway, 
    IClassificationGateway, 
    RunScanUseCase, 
    InspectTreeUseCase
)
# Implementations
from ..adapters.driven import (
    DetectionInternalGateway, 
    ClassificationInternalGateway
)
from ..ports.driving import ScannerController
from ..adapters.driving import register_commands


@dataclass(frozen=True, kw_only=True, slots=True)
class ScannerContainer:
    """
    Composition Root Facade for the Scanner Macro Context.
    Holds the main controller and exposes command registration logic.
    """
    controller: ScannerController

    def register_commands(self, app: typer.Typer) -> None:
        """
        Delegates command registration to the driving adapter logic.
        """
        register_commands(app, self.controller)


class ScannerProvider(Provider):
    """
    Orchestration Provider.
    Wires internal Gateways and Macro UseCases using auto-wiring.
    """
    
    scope = Scope.APP

    detection_gateway = provide(DetectionInternalGateway, provides=IDetectionGateway)
    classification_gateway = provide(ClassificationInternalGateway, provides=IClassificationGateway)

    # Macro UseCases (Auto-wired)
    run_scan_use_case = provide(RunScanUseCase)
    inspect_tree_use_case = provide(InspectTreeUseCase)

    # Main Controller (Auto-wired)
    controller = provide(ScannerController)

    container = provide(ScannerContainer)