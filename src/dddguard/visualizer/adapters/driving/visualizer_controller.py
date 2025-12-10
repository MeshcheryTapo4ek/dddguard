from dataclasses import dataclass
from pathlib import Path
from dddguard.shared import ConfigVo

from ...app import DrawArchitectureWorkflow, VisualizerAppError
from .errors import VisualizerAdapterError

@dataclass(frozen=True, kw_only=True, slots=True)
class VisualizerController:
    """
    Driving Adapter: Bridges CLI and Visualization Workflow.
    Handles exception translation (App -> Adapter).
    """
    workflow: DrawArchitectureWorkflow
    config: ConfigVo

    def draw_architecture(self, path: Path | None, output_path: Path) -> None:
        target_path = path if path else self.config.project.absolute_source_path
        
        if not target_path.exists():
            raise FileNotFoundError(f"Path not found: {target_path}")

        try:
            # Execute Workflow
            self.workflow.execute(target_path, output_path)
        except VisualizerAppError as e:
            raise VisualizerAdapterError(str(e)) from e