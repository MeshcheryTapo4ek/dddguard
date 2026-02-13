from collections.abc import Generator
from pathlib import Path
from typing import Protocol

from dddguard.shared.domain import ScannerConfig

from ..domain import SourceFileVo


class IProjectReader(Protocol):
    """
    Driven Port: Abstract interface for reading source files from the file system.
    """

    def read_project(
        self, scanner_config: ScannerConfig, target_path: Path, scan_all: bool = False
    ) -> Generator[SourceFileVo, None, None]:
        """
        Yields source files from the project.

        Args:
            target_path: Directory to start scanning.
            scan_all: If True, scans all text files. If False, scans only .py files.
        """
        ...

    def read_file(self, file_path: Path) -> SourceFileVo | None:
        """
        Reads a specific file by path.
        Returns None if file cannot be read or doesn't exist.
        """
        ...
