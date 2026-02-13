from dataclasses import dataclass
from pathlib import Path

from dddguard.scanner.ports.driving import ScannerFacade
from dddguard.shared.domain import CodeGraph

from ...app import IScannerGateway


@dataclass(frozen=True, kw_only=True, slots=True)
class ScannerAcl(IScannerGateway):
    """
    Driven Adapter (ACL): Anti-Corruption Layer.
    Refactored to be a thin wrapper.
    It protects the Linter from the *implementation* of the Scanner,
    but shares the *data contract* (CodeGraph).
    """

    scanner: ScannerFacade

    def get_project_graph(self, root_path: Path) -> CodeGraph:
        return self.scanner.scan_project(
            target_path=root_path,
            scan_all=False,
        )
