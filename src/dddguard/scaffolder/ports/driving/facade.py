from dataclasses import dataclass
from pathlib import Path

from ...app import CreateConfigUseCase, ScaffolderAppError


@dataclass(frozen=True, kw_only=True, slots=True)
class InitProjectResponseSchema:
    """
    Driving Schema: Output data for the Project Initialization operation.
    Decouples the Adapter from internal Domain types.
    """

    success: bool
    config_path: Path
    message: str
    error_details: str | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class ScaffolderFacade:
    """
    Driving Port: Entry point for Scaffolder operations.
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
                    message="Config already exists.",
                )

            # Invoke Application Logic
            self.create_config_use_case.execute(config_path)

            return InitProjectResponseSchema(
                success=True,
                config_path=config_path,
                message="Project initialized.",
            )

        except ScaffolderAppError as e:
            return InitProjectResponseSchema(
                success=False,
                config_path=config_path,
                message="Init failed.",
                error_details=str(e),
            )
        except Exception as e:
            return InitProjectResponseSchema(
                success=False,
                config_path=config_path,
                message="Unexpected init error.",
                error_details=str(e),
            )
