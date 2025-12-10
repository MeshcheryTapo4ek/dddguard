from dataclasses import dataclass
from pathlib import Path
from typing import List

from ...domain import ContextTower

from ...app import RenderingError, IDiagramRenderer


@dataclass(frozen=True, kw_only=True, slots=True)
class RenderDiagramUseCase:
    """
    App Use Case: Diagram Rendering.
    Takes the fully calculated geometric towers and persists them 
    using the injected infrastructure adapter (e.g., Draw.io XML).
    """
    renderer: IDiagramRenderer

    def execute(self, towers: List[ContextTower], output_path: Path) -> None:
        try:
            self.renderer.render(towers, output_path)
        except Exception as e:
            # Wrap infrastructure errors into clean App Errors
            raise RenderingError(str(output_path), str(e)) from e