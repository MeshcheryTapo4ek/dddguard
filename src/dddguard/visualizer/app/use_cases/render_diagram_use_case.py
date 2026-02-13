from dataclasses import dataclass
from pathlib import Path

from ...app import IDiagramRenderer, RenderingError
from ...domain import ContextTower, VisualizationConfig


@dataclass(frozen=True, kw_only=True, slots=True)
class RenderDiagramUseCase:
    """
    App Use Case: Diagram Rendering.
    Takes the fully calculated geometric towers and persists them
    using the injected infrastructure adapter (e.g., Draw.io XML).
    """

    renderer: IDiagramRenderer

    def execute(
        self,
        towers: list[ContextTower],
        output_path: Path,
        option: VisualizationConfig,
    ) -> None:
        try:
            self.renderer.render(towers, output_path, option)
        except Exception as e:
            raise RenderingError(str(output_path), original_error=e) from e
