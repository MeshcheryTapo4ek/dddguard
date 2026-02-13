from typing import Protocol

from ..domain import ScaffolderFileVo


class IFileSystemGateway(Protocol):
    """
    Abstract Port for File System I/O.
    """

    def write_file(self, file_vo: ScaffolderFileVo) -> None: ...
