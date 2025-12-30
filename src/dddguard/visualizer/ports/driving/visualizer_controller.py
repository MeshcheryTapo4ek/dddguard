from dataclasses import dataclass
from pathlib import Path
from dddguard.shared import ConfigVo

from ...app import DrawArchitectureWorkflow, VisualizerAppError
from ...domain import VisualizationOptions
from .schemas import DrawOptionsDto
from .errors import VisualizerAdapterError


@dataclass(frozen=True, kw_only=True, slots=True)
class VisualizerController:
    """
    Driving Adapter: Bridges CLI and Visualization Workflow.
    """

    workflow: DrawArchitectureWorkflow
    config: ConfigVo

    def draw_architecture(self, path: Path | None, dto: DrawOptionsDto) -> None:
        target_path = path if path else self.config.project.absolute_source_path

        if not target_path.exists():
            raise FileNotFoundError(f"Path not found: {target_path}")

        domain_options = VisualizationOptions(
            show_errors=dto.show_errors,
            hide_root_arrows=dto.hide_root_arrows,
            hide_shared_arrows=dto.hide_shared_arrows,
            output_file=dto.output_file,
        )

        try:
            self.workflow.execute(target_path, domain_options)
        except VisualizerAppError as e:
            raise VisualizerAdapterError(str(e)) from e