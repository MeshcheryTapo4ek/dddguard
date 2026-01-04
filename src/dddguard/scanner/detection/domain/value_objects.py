from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import List, Optional


@dataclass(frozen=True, kw_only=True, slots=True)
class SourceFileVo:
    path: Path
    content: str


@dataclass(frozen=True, kw_only=True, slots=True)
class ImportedModuleVo:
    module_path: str
    lineno: int
    is_relative: bool
    imported_names: List[str] = field(default_factory=list)


@dataclass(frozen=True, kw_only=True, slots=True)
class ScannedModuleVo:
    logical_path: str
    file_path: Path
    content: str
    raw_imports: List[ImportedModuleVo] = field(default_factory=list)

    @property
    def is_package(self) -> bool:
        return self.file_path.name == "__init__.py"


@dataclass(frozen=True, kw_only=True, slots=True)
class DependencyLink:
    source_module: str
    target_module: str
    imported_symbols: List[str] = field(default_factory=list)


@dataclass(frozen=True, kw_only=True) # Removed slots=True for caching
class ScanStatisticsVo:
    total_files: int
    total_modules: int
    total_relations: int

    @cached_property
    def relations_per_module(self) -> float:
        """Example of a cached metric."""
        if self.total_modules == 0:
            return 0.0
        return round(self.total_relations / self.total_modules, 2)


@dataclass(frozen=True)
class ScanResult:
    graph: "DependencyGraph"
    source_tree: dict
    stats: ScanStatisticsVo


@dataclass(frozen=True, kw_only=True, slots=True)
class PathFilter:
    """
    Encapsulates logic for filtering files based on scope/focus.
    Replaces loose 'focus_path' and 'include_paths' arguments.
    """
    focus_path: Path
    include_paths: Optional[List[Path]] = None

    def is_relevant(self, file_path: Path) -> bool:
        """
        Determines if a physical file path is part of the current analysis scope.
        """
        # 1. Must be within the main focus path
        # Convert to str for fast prefix checking (faster than pathlib.is_relative_to in loops)
        f_path_str = str(file_path)
        
        if not f_path_str.startswith(str(self.focus_path)):
            return False
        
        # 2. If allow-list is present, must match at least one
        if self.include_paths:
            return any(f_path_str.startswith(str(inc)) for inc in self.include_paths)
            
        return True