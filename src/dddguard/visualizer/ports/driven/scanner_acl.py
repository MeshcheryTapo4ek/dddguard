from dataclasses import dataclass
from pathlib import Path

from dddguard.scanner.ports.driving.scanner_facade import ScannerFacade

# 1. External Imports (Shared & Facade)
from dddguard.shared.domain import CodeGraph

# 2. Local Imports
from ...app.interfaces import IScannerGateway


@dataclass(frozen=True, kw_only=True, slots=True)
class ScannerAcl(IScannerGateway):
    """
    Driven Port: Anti-Corruption Layer (Thin Wrapper).
    Delegates directly to the ScannerFacade and returns the Shared Kernel CodeGraph.
    """

    _scanner_facade: ScannerFacade

    def get_dependency_graph(self, root_path: Path) -> CodeGraph:
        return self._scanner_facade.scan_project(
            target_path=root_path,
            scan_all=False,
            import_depth=0,
            include_assets=True,
        )
