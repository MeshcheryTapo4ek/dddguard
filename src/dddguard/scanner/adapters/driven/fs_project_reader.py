import os
import fnmatch
from pathlib import Path
from typing import Generator, Set
from dataclasses import dataclass

from ...app import IProjectReader
from ...domain import SourceFileVo
from dddguard.shared import ConfigVo


@dataclass(frozen=True, slots=True, kw_only=True)
class FSProjectReader(IProjectReader):
    """
    Driven Adapter: Reads source code from filesystem using configuration rules.
    Capable of safe multi-format scanning.
    """
    config: ConfigVo

    def read_project(
        self, 
        root_path: Path, 
        scan_all: bool = False
    ) -> Generator[SourceFileVo, None, None]:
        
        exclude_dirs = self.config.scanner.exclude_dirs
        ignore_files = self.config.scanner.ignore_files
        binary_exts = self.config.scanner.binary_extensions
        max_size = self.config.scanner.max_file_size_bytes

        for root, dirs, files in os.walk(root_path):
            # 1. Prune excluded directories in-place
            dirs[:] = [
                d for d in dirs 
                if d not in exclude_dirs and not d.startswith(".")
            ]

            path_parts = Path(root).parts

            for file in files:
                file_lower = file.lower()
                
                # --- [HOTFIX] SKIP INFRASTRUCTURE ERRORS ---
                if file_lower == "errors.py":
                    if "adapters" in path_parts or "ports" in path_parts:
                        continue
                # -------------------------------------------

                # 2. Extension Filtering
                if not scan_all:
                    # Strict Python mode
                    if not file.endswith(".py"):
                        continue
                else:
                    # "All" mode: Skip known binaries/media
                    _, ext = os.path.splitext(file_lower)
                    if ext in binary_exts:
                        continue

                # 3. Config Ignore check (patterns)
                if self._should_ignore(file, ignore_files):
                    continue

                file_path = Path(root) / file
                
                # 4. Size Check (Performance/Safety)
                try:
                    stat = file_path.stat()
                    if stat.st_size > max_size:
                        continue
                except OSError:
                    continue

                # 5. Read Content
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    yield SourceFileVo(path=file_path, content=content)
                
                except UnicodeDecodeError:
                    continue
                except Exception:
                    continue

    def _should_ignore(self, filename: str, ignore_patterns: Set[str]) -> bool:
        """Helper to match filename against set of glob patterns or exact names."""
        if filename in ignore_patterns:
            return True
        for pattern in ignore_patterns:
            if fnmatch.fnmatch(filename, pattern):
                return True
        return False