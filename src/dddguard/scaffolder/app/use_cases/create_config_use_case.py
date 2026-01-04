from dataclasses import dataclass
from pathlib import Path

from ..interfaces import IFileSystemGateway
from ..errors import ScaffolderAppError
from ...domain import ScaffolderFileVo
from ...domain.assets import DEFAULT_CONFIG_TEMPLATE


@dataclass(frozen=True, kw_only=True, slots=True)
class CreateConfigUseCase:
    """
    App Service: Generates the default configuration file for the project.
    """

    fs_gateway: IFileSystemGateway

    def execute(self, target_path: Path) -> None:
        """
        Creates the config file at the specified path.
        Injects the current working directory as root_dir in the template.
        """
        try:
            cwd_str = Path.cwd().as_posix()

            content = DEFAULT_CONFIG_TEMPLATE.format(root_dir=cwd_str)

            file_vo = ScaffolderFileVo(path=target_path, content=content)

            self.fs_gateway.write_file(file_vo)

        except Exception as e:
            # Updated: Pass original_error for traceability
            raise ScaffolderAppError(
                message=f"Failed to generate config: {e}", 
                original_error=e
            ) from e