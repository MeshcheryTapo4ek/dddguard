from dataclasses import dataclass

from dishka import Container, make_container

from dddguard.linter.provider import LinterContainer, LinterProvider
from dddguard.scaffolder.provider import ScaffolderContainer, ScaffolderProvider
from dddguard.scanner.classification.provider import ClassificationProvider
from dddguard.scanner.detection.provider import DetectionProvider
from dddguard.scanner.provider import ScannerContainer, ScannerProvider
from dddguard.shared.provider import SharedProvider
from dddguard.visualizer.provider import VisualizerContainer, VisualizerProvider


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
    return make_container(
        # Shared
        SharedProvider(),
        # Scanner Macro Context & Sub-Contexts
        ScannerProvider(),
        DetectionProvider(),  # Required to build DetectionFacade
        ClassificationProvider(),  # Required to build ClassificationFacade
        # Other Contexts
        ScaffolderProvider(),
        LinterProvider(),
        VisualizerProvider(),
    )
