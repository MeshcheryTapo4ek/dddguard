from dataclasses import dataclass
from pathlib import Path

from dddguard.shared.domain import CodeGraph, ScannerConfig

from ..interfaces import IClassificationGateway, IDetectionGateway


@dataclass(frozen=True, kw_only=True, slots=True)
class InspectTreeUseCase:
    """
    Macro UseCase: Raw Architectural Inspection.

    Performs a direct "scan & classify" pass to visualize the project structure
    with architectural annotations (Passports) without any filtering.

    **Purpose:**
    Answers: *"What is the architectural structure of this codebase?"*

    **Pipeline:**
    1.  **Detection:** Physical scan of the source directory.
    2.  **Classification:** Architecture assignment.
    3.  **Finalization:** Mark ALL nodes as visible (no filtering).
    """

    detection_gateway: IDetectionGateway
    classification_gateway: IClassificationGateway

    def __call__(
        self,
        scanner_config: ScannerConfig,
        source_dir: Path,
        scan_all: bool = False,
    ) -> CodeGraph:
        """
        Executes the inspection.

        :param scanner_config: Configuration for the scanning process.
        :param source_dir: The project source root to inspect.
        :param scan_all: If True, includes non-code assets (txt, md, config, etc.).
        :return: A fully visible (FINALIZED) CodeGraph.
        """
        # 1. DETECT (Physical Scan)
        detected_graph = self.detection_gateway.scan(
            scanner_config=scanner_config,
            target_path=source_dir,
            scan_all=scan_all,
        )

        # 2. CLASSIFY (Architectural Assignment)
        classified_graph = self.classification_gateway.classify(
            graph=detected_graph,
            source_dir=source_dir,
        )

        # 3. FINALIZE (Visibility)
        # Mark all nodes as FINALIZED (no filtering applied)
        for node in classified_graph.nodes.values():
            node.finalize()

        return classified_graph
