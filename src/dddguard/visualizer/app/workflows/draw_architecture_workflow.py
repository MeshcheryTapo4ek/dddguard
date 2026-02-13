from dataclasses import dataclass
from pathlib import Path

from ...domain import VisualizationConfig
from ..errors import VisualizerAppError
from ..interfaces import IScannerGateway
from ..use_cases.calculate_layout_use_case import CalculateLayoutUseCase
from ..use_cases.render_diagram_use_case import RenderDiagramUseCase


@dataclass(frozen=True, kw_only=True, slots=True)
class DrawArchitectureWorkflow:
    """
    Workflow: Orchestrates the End-to-End process of visualizing a project.
    Pipeline: Scan -> Calculate Layout -> Render.
    """

    scanner_gateway: IScannerGateway
    calculate_layout: CalculateLayoutUseCase
    render_diagram: RenderDiagramUseCase

    def execute(self, root_path: Path, option: VisualizationConfig) -> None:
        # 1. Scan Project
        try:
            graph = self.scanner_gateway.get_dependency_graph(root_path)
        except Exception as e:
            raise VisualizerAppError(
                message=f"Workflow failed at Scanning stage: {e}", original_error=e
            ) from e

        # 2. Calculate Layout
        towers = self.calculate_layout.execute(graph)

        # 3. Render Diagram
        output = Path(option.output_file)
        self.render_diagram.execute(towers, output, option)
