from typing import Protocol, Dict, Any, List
from pathlib import Path

from ..domain.value_objects import DetectionResultVo, ClassificationResultVo
from dddguard.shared.domain import ComponentPassport


class IDetectionGateway(Protocol):
    """
    Interface for interacting with the Detection Bounded Context.
    Returns Domain VOs, not Port Schemas.
    """
    def scan(
        self,
        target_path: Path | None,
        dirs_only: bool,
        scan_all: bool,
        import_depth: int,
        focus_path: Path | None,
        include_paths: List[Path] | None,
    ) -> DetectionResultVo:
        ...


class IClassificationGateway(Protocol):
    """
    Interface for interacting with the Classification Bounded Context.
    Returns Domain VOs, not Port Schemas.
    """
    def classify(self, raw_graph_nodes: Dict[str, Any]) -> ClassificationResultVo:
        ...

    def identify_component(self, file_path: Path) -> ComponentPassport:
        """
        Identifies the architectural role of a single file/directory.
        """
        ...