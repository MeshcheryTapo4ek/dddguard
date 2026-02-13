from pathlib import Path
from typing import Protocol

from dddguard.shared.domain import CodeGraph

from ..domain import ContextTower, VisualizationConfig


class IDiagramRenderer(Protocol):
    def render(
        self,
        towers: list[ContextTower],
        output_path: Path,
        options: VisualizationConfig,
    ) -> None: ...


class IScannerGateway(Protocol):
    """
    Application Port: Abstract interface for retrieving the project code graph.
    Uses Shared Kernel's CodeGraph directly.
    """

    def get_dependency_graph(self, root_path: Path) -> CodeGraph: ...
