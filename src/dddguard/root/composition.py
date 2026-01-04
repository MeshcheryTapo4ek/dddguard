from dataclasses import dataclass
from dishka import make_container, Container

from dddguard.scanner import ScannerProvider, ScannerContainer
# Import sub-context providers to satisfy dependencies of the Macro Context
from dddguard.scanner.detection.composition import DetectionProvider
from dddguard.scanner.classification.composition import ClassificationProvider

from dddguard.scaffolder import ScaffolderProvider, ScaffolderContainer
from dddguard.linter import LinterProvider, LinterContainer
from dddguard.visualizer import VisualizerProvider, VisualizerContainer

from dddguard.shared.composition import SharedConfigProvider


@dataclass(frozen=True, kw_only=True)
class ApplicationContainer:
    """
    Root Container Facade.
    """
    scanner: ScannerContainer
    scaffolder: ScaffolderContainer
    linter: LinterContainer
    visualizer: VisualizerContainer


def build_app_container() -> Container:
    """
    Initializes Dishka DI Container with all context providers.
    """
    container = make_container(
        # Shared
        SharedConfigProvider(),
        
        # Scanner Macro Context & Sub-Contexts
        ScannerProvider(),
        DetectionProvider(),        # Required to build DetectionController
        ClassificationProvider(),   # Required to build ClassificationController
        
        # Other Contexts
        ScaffolderProvider(),
        LinterProvider(),
        VisualizerProvider(),
    )
    return container