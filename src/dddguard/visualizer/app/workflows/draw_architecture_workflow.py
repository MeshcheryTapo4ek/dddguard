from dataclasses import dataclass
from pathlib import Path

from ..interfaces import IScannerGateway
from ..use_cases.calculate_layout_use_case import CalculateLayoutUseCase
from ..use_cases.render_diagram_use_case import RenderDiagramUseCase
from ..errors import VisualizerAppError

from ...domain import VisualizationOptions


@dataclass(frozen=True, kw_only=True, slots=True)
class DrawArchitectureWorkflow:
    """
    Workflow: Orchestrates the End-to-End process of visualizing a project.
    Pipeline: Scan -> Calculate Layout -> Render.
    """

    scanner_gateway: IScannerGateway
    calculate_layout: CalculateLayoutUseCase
    render_diagram: RenderDiagramUseCase

    def execute(self, root_path: Path, options: VisualizationOptions) -> None:
        # 1. Scan Project
        try:
            graph = self.scanner_gateway.get_dependency_graph(root_path)
        except Exception as e:
            raise VisualizerAppError(f"Workflow failed at Scanning stage: {e}") from e

        # 2. Calculate Layout
        towers = self.calculate_layout.execute(graph)

        # 3. Render Diagram
        output = Path(options.output_file)
        self.render_diagram.execute(towers, output, options)