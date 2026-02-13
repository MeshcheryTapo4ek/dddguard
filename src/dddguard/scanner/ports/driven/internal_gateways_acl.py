from dataclasses import dataclass
from pathlib import Path

from dddguard.shared.domain import CodeGraph, ScannerConfig

from ...app import IClassificationGateway, IDetectionGateway
from ...classification.ports.driving.facade import ClassificationFacade
from ...detection.ports.driving.facade import DetectionFacade


@dataclass(frozen=True, kw_only=True, slots=True)
class DetectionInternalGateway(IDetectionGateway):
    """
    Adapter: Connects Scanner App to Detection Context.
    """

    facade: DetectionFacade

    def scan(self, scanner_config: ScannerConfig, target_path: Path, scan_all: bool) -> CodeGraph:
        # Maps the generic interface call to the specific Facade method
        return self.facade.scan_physical_project(
            scanner_config=scanner_config,
            target_path=target_path,
            scan_all=scan_all,
        )


@dataclass(frozen=True, kw_only=True, slots=True)
class ClassificationInternalGateway(IClassificationGateway):
    """
    Adapter: Connects Scanner App to Classification Context.
    """

    facade: ClassificationFacade

    def classify(self, graph: CodeGraph, source_dir: Path | None = None) -> CodeGraph:
        # Maps the generic interface call to the specific Facade method
        return self.facade.classify_graph(graph=graph, source_dir=source_dir)
