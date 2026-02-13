from dataclasses import dataclass

import typer
from dishka import Provider, Scope, provide

from .adapters.driving import register_commands

# Interfaces
from .app import (
    DiscoverContextsUseCase,
    IClassificationGateway,
    IDetectionGateway,
    InspectTreeUseCase,
    RunScanUseCase,
)

# Implementations
from .ports.driven.internal_gateways_acl import (
    ClassificationInternalGateway,
    DetectionInternalGateway,
)
from .ports.driving import ScannerFacade


@dataclass(frozen=True, kw_only=True, slots=True)
class ScannerContainer:
    """
    Composition Root Facade for the Scanner Macro Context.
    """

    facade: ScannerFacade

    def register_commands(self, app: typer.Typer) -> None:
        register_commands(app, self.facade)


class ScannerProvider(Provider):
    """
    Orchestration Provider.
    Wires internal Gateways, Domain Services, and Macro UseCases.
    """

    scope = Scope.APP

    # Internal Gateways (ACL)
    detection_gateway = provide(DetectionInternalGateway, provides=IDetectionGateway)
    classification_gateway = provide(ClassificationInternalGateway, provides=IClassificationGateway)

    # Macro UseCases
    run_scan_use_case = provide(RunScanUseCase)
    inspect_tree_use_case = provide(InspectTreeUseCase)
    discover_contexts_use_case = provide(DiscoverContextsUseCase)

    # Main facade
    facade = provide(ScannerFacade)

    container = provide(ScannerContainer)
