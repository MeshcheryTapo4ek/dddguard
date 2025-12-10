from dataclasses import dataclass
from pathlib import Path

from dddguard.scanner import ScanProjectUseCase, ScannerAppError

from ..use_cases.calculate_layout_use_case import CalculateLayoutUseCase
from ..use_cases.render_diagram_use_case import RenderDiagramUseCase

from ...app.errors import VisualizerAppError


@dataclass(frozen=True, kw_only=True, slots=True)
class DrawArchitectureWorkflow:
    """
    Workflow: Orchestrates the End-to-End process of visualizing a project.
    Pipeline: Scan -> Calculate Layout -> Render.
    """
    scan_project: ScanProjectUseCase
    calculate_layout: CalculateLayoutUseCase
    render_diagram: RenderDiagramUseCase

    def execute(self, root_path: Path, output_path: Path) -> None:
        # 1. Scan Project (Cross-Context Call)
        try:
            scan_result = self.scan_project.execute(root_path)
        except ScannerAppError as e:
            raise VisualizerAppError(f"Workflow failed at Scanning stage: {e}") from e

        # 2. Calculate Layout (Pure Logic)
        towers = self.calculate_layout.execute(scan_result.graph)

        # 3. Render Diagram (Side Effect)
        self.render_diagram.execute(towers, output_path)