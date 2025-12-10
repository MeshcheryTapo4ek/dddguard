from dataclasses import dataclass
from pathlib import Path

from ..interfaces import IFileSystemGateway
from ...domain import RenderedFileVo
from ...adapters.assets import DEFAULT_CONFIG_TEMPLATE
from ..errors import ScaffolderAppError


@dataclass(frozen=True, kw_only=True, slots=True)
class CreateConfigUseCase:
    """
    App Service: Generates a standalone configuration file.
    """
    fs_gateway: IFileSystemGateway

    def execute(self, output_path: Path) -> None:
        """
        Creates the config file at the specified path.
        Injects the current working directory as root_dir.
        """
        try:
            target_root = output_path.parent
            filename = output_path.name
            
            # Inject absolute path of the current directory
            cwd_str = Path.cwd().as_posix()
            content = DEFAULT_CONFIG_TEMPLATE.format(root_dir=cwd_str)

            file_vo = RenderedFileVo(
                relative_path=Path(filename),
                content=content
            )

            self.fs_gateway.write_files(target_root, [file_vo])
            
        except Exception as e:
            raise ScaffolderAppError(f"Failed to generate config: {e}") from e