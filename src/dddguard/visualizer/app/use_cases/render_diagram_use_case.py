from dataclasses import dataclass
from pathlib import Path
from typing import List

from ...domain import ContextTower, VisualizationOptions

from ...app import RenderingError, IDiagramRenderer


@dataclass(frozen=True, kw_only=True, slots=True)
class RenderDiagramUseCase:
    """
    App Use Case: Diagram Rendering.
    Takes the fully calculated geometric towers and persists them
    using the injected infrastructure adapter (e.g., Draw.io XML).
    """

    renderer: IDiagramRenderer

    def execute(self, towers: List[ContextTower], output_path: Path, options: VisualizationOptions) -> None:
        try:
            self.renderer.render(towers, output_path, options)
        except Exception as e:
            raise RenderingError(str(output_path), original_error=e) from e