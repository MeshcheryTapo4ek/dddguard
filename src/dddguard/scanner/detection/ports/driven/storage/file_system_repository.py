from pathlib import Path
from typing import Generator, Optional, Set
from dataclasses import dataclass

from dddguard.shared.domain import ConfigVo
from ....app import IProjectReader
from ....domain import SourceFileVo


@dataclass(frozen=True, slots=True, kw_only=True)
class FileSystemRepository(IProjectReader):
    """
    Driven Port Implementation: Translates OS filesystem data into Domain SourceFileVo.
    Refactored to use pathlib for cleaner iteration and path handling.
    """

    config: ConfigVo

    def read_project(
        self, root_path: Path, scan_all: bool = False
    ) -> Generator[SourceFileVo, None, None]:
        # 1. Handle Single File case
        if root_path.is_file():
            if source_file := self._read_file_safe(root_path, scan_all):
                yield source_file
            return

        # 2. Prepare Filters
        exclude_dirs = self.config.scanner.exclude_dirs
        ignore_files = self.config.scanner.ignore_files
        binary_exts = self.config.scanner.binary_extensions
        max_size = self.config.scanner.max_file_size_bytes

        # 3. Recursive Traversal (Concise Pathlib replacement for os.walk)
        for file_path in self._walk_pathlib(root_path, exclude_dirs):
            
            # Filter: Ignored Filenames
            if file_path.name in ignore_files:
                continue

            # Filter: Extension Strategy
            if not scan_all and file_path.suffix != ".py":
                continue

            if scan_all and file_path.suffix.lower() in binary_exts:
                continue

            # Filter: Size & Content
            try:
                if file_path.stat().st_size > max_size:
                    continue

                if content := self._read_content(file_path):
                    yield SourceFileVo(path=file_path, content=content)

            except OSError:
                continue

    def read_file(self, file_path: Path) -> Optional[SourceFileVo]:
        return self._read_file_safe(file_path, scan_all=True)

    def _walk_pathlib(self, path: Path, exclude_dirs: Set[str]) -> Generator[Path, None, None]:
        """
        Custom recursive generator using iterdir().
        Replacement for os.walk that allows pruning directories efficiently.
        """
        try:
            for entry in path.iterdir():
                # Prune directories immediately
                if entry.name in exclude_dirs or entry.name.startswith("."):
                    continue
                
                if entry.is_dir():
                    yield from self._walk_pathlib(entry, exclude_dirs)
                elif entry.is_file():
                    yield entry
        except (PermissionError, OSError):
            return

    def _read_content(self, file_path: Path) -> str | None:
        try:
            return file_path.read_text(encoding="utf-8", errors="strict")
        except (UnicodeDecodeError, OSError):
            return None

    def _read_file_safe(self, path: Path, scan_all: bool) -> SourceFileVo | None:
        if not scan_all and path.suffix != ".py":
            return None

        content = self._read_content(path)
        if content is not None:
            return SourceFileVo(path=path, content=content)
        return None