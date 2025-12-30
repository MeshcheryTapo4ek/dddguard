from dataclasses import dataclass
from pathlib import Path

from ...app import CreateConfigUseCase, ScaffolderAppError
from .schemas import InitProjectResponseSchema


@dataclass(frozen=True, kw_only=True, slots=True)
class ScaffolderController:
    """
    Driving Port: Entry point for Scaffolder operations.
    Translates external intents (Init Project) into Application Commands.
    """

    create_config_use_case: CreateConfigUseCase

    def init_project(self, target_root: Path) -> InitProjectResponseSchema:
        """
        Orchestrates the initialization of the project configuration.
        Handles Application Errors and translates them into a Response Schema.
        """
        # Define the standard location for the config
        config_path = target_root / "docs" / "dddguard" / "config.yaml"

        try:
            # Check pre-conditions (Logic owned by Port/App boundary)
            # Note: We perform a read-check here to return a clean failure schema
            # if the file exists, rather than crashing in the adapter.
            if config_path.exists():
                return InitProjectResponseSchema(
                    success=False,
                    config_path=config_path,
                    message="Configuration file already exists.",
                )

            # Invoke Application Logic
            self.create_config_use_case.execute(config_path)

            return InitProjectResponseSchema(
                success=True,
                config_path=config_path,
                message="Project initialized successfully.",
            )

        except ScaffolderAppError as e:
            # Capture expected App errors and return as Schema
            return InitProjectResponseSchema(
                success=False,
                config_path=config_path,
                message="Initialization failed due to an application error.",
                error_details=str(e),
            )
        except Exception as e:
            # Capture unexpected errors
            return InitProjectResponseSchema(
                success=False,
                config_path=config_path,
                message="Critical unexpected error during initialization.",
                error_details=str(e),
            )
