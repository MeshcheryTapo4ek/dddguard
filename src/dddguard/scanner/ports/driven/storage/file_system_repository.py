import os
from pathlib import Path
from typing import Generator, Optional
from dataclasses import dataclass

from dddguard.shared.domain import ConfigVo
from ....app import IProjectReader
from ....domain import SourceFileVo


@dataclass(frozen=True, slots=True, kw_only=True)
class FileSystemRepository(IProjectReader):
    """
    Driven Port Implementation: Translates OS filesystem data into Domain SourceFileVo.
    Acts as a Read-Only Repository for Source Files.
    """

    config: ConfigVo

    def read_project(
        self, root_path: Path, scan_all: bool = False
    ) -> Generator[SourceFileVo, None, None]:
        """
        Recursively scans the directory, filtering out ignored items defined in Config.
        Yields PURE domain objects (SourceFileVo).
        """
        # 1. Handle Single File case immediately
        if root_path.is_file():
            source_file = self._read_file_safe(root_path, scan_all)
            if source_file:
                yield source_file
            return

        # 2. Prepare Filters for performance
        exclude_dirs = self.config.scanner.exclude_dirs
        ignore_files = self.config.scanner.ignore_files
        binary_exts = self.config.scanner.binary_extensions
        max_size = self.config.scanner.max_file_size_bytes

        # 3. Walk the tree
        for current_root, dirs, files in os.walk(root_path):
            # A. Prune directories in-place to prevent recursion into them
            # We filter out if name is in exclude_dirs OR starts with "." (hidden)
            dirs[:] = [
                d for d in dirs if d not in exclude_dirs and not d.startswith(".")
            ]

            current_root_path = Path(current_root)

            for filename in files:
                file_path = current_root_path / filename

                # B. Fast Filters (Name & Extension)
                if filename in ignore_files:
                    continue

                # Strict Mode: Only Python
                if not scan_all and file_path.suffix != ".py":
                    continue

                # All Mode: Skip known binaries
                if scan_all and file_path.suffix.lower() in binary_exts:
                    continue

                # C. IO Checks (Size & Content)
                try:
                    stat = file_path.stat()
                    if stat.st_size > max_size:
                        # Skip files compliant with size limit
                        continue

                    content = self._read_content(file_path)
                    if content is not None:
                        yield SourceFileVo(path=file_path, content=content)

                except OSError:
                    # Permission denied or broken link
                    continue

    def read_file(self, file_path: Path) -> Optional[SourceFileVo]:
        """
        Reads a specific file by path (Implementation of IProjectReader).
        Strictly reads Python files for resolution logic unless we generalize later.
        """
        return self._read_file_safe(file_path, scan_all=True)

    def _read_content(self, file_path: Path) -> str | None:
        """
        Attempts to read file content as UTF-8 text.
        Returns None if file appears binary or unreadable.
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="strict") as f:
                return f.read()
        except UnicodeDecodeError:
            return None
        except Exception:
            return None

    def _read_file_safe(self, path: Path, scan_all: bool) -> SourceFileVo | None:
        """Helper for the single-file input case."""
        if not scan_all and path.suffix != ".py":
            return None

        content = self._read_content(path)
        if content is not None:
            return SourceFileVo(path=path, content=content)
        return None