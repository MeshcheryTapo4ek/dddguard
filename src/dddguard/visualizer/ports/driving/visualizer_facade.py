from dataclasses import dataclass
from pathlib import Path

from dddguard.shared.domain import ConfigVo

from ...app import DrawArchitectureWorkflow
from ...domain import VisualizationConfig


@dataclass(frozen=True, slots=True, kw_only=True)
class DrawOptionsDto:
    """
    Driving DTO: Represents the user's choices from the UI.
    """

    # Visibility Toggles
    show_errors: bool = False

    # Directional Filters
    hide_root_arrows: bool = True  # Hide arrows FROM Root (Wiring noise)
    hide_shared_arrows: bool = True  # Hide arrows TO Shared (Usage noise)

    # Output
    output_file: str = "architecture.drawio"


@dataclass(frozen=True, kw_only=True, slots=True)
class VisualizerFacade:
    """
    Driving Adapter: Bridges CLI and Visualization Workflow.
    """

    workflow: DrawArchitectureWorkflow
    config: ConfigVo

    def draw_architecture(self, path: Path | None, dto: DrawOptionsDto) -> None:
        target_path = path if path else self.config.project.absolute_source_path

        if not target_path:
            raise FileNotFoundError("No target path provided and no source_dir configured")
        if not target_path.exists():
            raise FileNotFoundError(f"Path not found: {target_path}")

        domain_options = VisualizationConfig(
            show_errors=dto.show_errors,
            hide_root_arrows=dto.hide_root_arrows,
            hide_shared_arrows=dto.hide_shared_arrows,
            output_file=dto.output_file,
        )

        self.workflow.execute(target_path, domain_options)
