from typing import Protocol, List
from pathlib import Path

from ..domain import ContextTower, DependencyGraph, VisualizationOptions


class IDiagramRenderer(Protocol):
    def render(self, towers: List[ContextTower], output_path: Path, options: VisualizationOptions) -> None: ...


class IScannerGateway(Protocol):
    """
    Application Port: Abstract interface for retrieving the project dependency graph.
    Returns the VISUALIZER'S local Graph domain object.
    """

    def get_dependency_graph(self, root_path: Path) -> DependencyGraph: ...