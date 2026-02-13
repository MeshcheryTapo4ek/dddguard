from dishka import Provider, Scope, provide

from .app import (
    IProjectReader,
    ScanProjectUseCase,
)
from .ports.driven.storage.file_system_repository import FileSystemRepository
from .ports.driving.facade import DetectionFacade


class DetectionProvider(Provider):
    """
    DI Provider for the Detection Bounded Context.
    Only provides Stateful Components (Adapters/UseCases).
    Domain Services are now internal to UseCases.
    """

    scope = Scope.APP

    # Driven Adapters
    reader = provide(FileSystemRepository, provides=IProjectReader)

    # Application Services
    scan_use_case = provide(ScanProjectUseCase)

    # Driving Port
    facade = provide(DetectionFacade)
