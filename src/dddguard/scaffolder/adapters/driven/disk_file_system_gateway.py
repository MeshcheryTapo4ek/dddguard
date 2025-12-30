from dataclasses import dataclass

from ...app import IFileSystemGateway, ScaffolderAppError
from ...domain import ScaffolderFileVo


@dataclass(frozen=True, kw_only=True, slots=True)
class DiskFileSystemGateway(IFileSystemGateway):
    """
    Driven Adapter: Physical File System implementation.
    """

    def write_file(self, file_vo: ScaffolderFileVo) -> None:
        try:
            full_path = file_vo.path.resolve()

            # Ensure directory exists
            if not full_path.parent.exists():
                full_path.parent.mkdir(parents=True, exist_ok=True)

            with open(full_path, "w", encoding="utf-8") as f:
                f.write(file_vo.content)

        except Exception as e:
            raise ScaffolderAppError(f"IO Error writing config to {file_vo.path}: {e}")
