from typing import Protocol, Generator
from pathlib import Path

from ..domain import SourceFileVo


class IProjectReader(Protocol):
    """
    Port for reading project source files.
    """

    def read_project(
        self, 
        root_path: Path, 
        scan_all: bool = False
    ) -> Generator[SourceFileVo, None, None]: 
        """
        Yields source files from the project.
        
        Args:
            root_path: Directory to start scanning.
            scan_all: If True, scans all text files (respecting ignores). 
                      If False, scans only .py files.
        """
        ...