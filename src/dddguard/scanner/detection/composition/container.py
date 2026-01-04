from dishka import Provider, Scope, provide

from ..app import (
    ScanProjectUseCase,
    IProjectReader,
)
from ..domain import (
    AstImportParserService,
    ModuleResolutionService,
    DependencyExpansionService,
)
from ..ports.driven.storage.file_system_repository import FileSystemRepository
from ..ports.driving import DetectionController


class DetectionProvider(Provider):
    """
    DI Provider for the Detection Bounded Context.
    Provides services for physical code scanning and graph building.
    """

    scope = Scope.APP
    reader = provide(FileSystemRepository, provides=IProjectReader)

    # Domain Services 
    parser = provide(AstImportParserService)
    module_resolver = provide(ModuleResolutionService)
    dependency_service = provide(DependencyExpansionService)

    # Application Service
    scan_use_case = provide(ScanProjectUseCase)

    # Driving Port
    controller = provide(DetectionController)