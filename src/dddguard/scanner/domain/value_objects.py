from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Dict, Optional

from dddguard.shared.domain import (
    ScopeEnum,
    LayerEnum,
    ComponentPassport,
    ComponentType,
)


@dataclass(frozen=True, kw_only=True, slots=True)
class SourceFileVo:
    """Represents a source file and its content."""

    path: Path
    content: str


@dataclass(frozen=True, kw_only=True, slots=True)
class ClassificationResultVo:
    """Result of the SRM v2.0 identification engine."""

    scope: ScopeEnum
    layer: LayerEnum
    component_type: ComponentType
    context_name: str
    is_definitive: bool = False


@dataclass(frozen=True, kw_only=True, slots=True)
class ImportedModuleVo:
    """Raw import statement metadata."""

    module_path: str
    lineno: int
    is_relative: bool
    imported_names: List[str] = field(default_factory=list)


@dataclass(frozen=True, kw_only=True, slots=True)
class ScannedModuleVo:
    """
    Aggregate Object representing a fully analyzed Python module/package.
    Contains raw data before Graph Node construction.
    """

    logical_path: str
    file_path: Path
    content: str
    classification: ClassificationResultVo
    raw_imports: List[ImportedModuleVo] = field(default_factory=list)

    @property
    def is_package(self) -> bool:
        return self.file_path.name == "__init__.py"


@dataclass(frozen=True, kw_only=True, slots=True)
class DependencyLink:
    """
    Uni-directional dependency between two modules.
    """

    source_module: str
    target_module: str
    target_context: Optional[str] = None
    target_layer: Optional[str] = None
    target_type: Optional[str] = None
    
    # NEW: Track which specific symbols are imported through this link
    imported_symbols: List[str] = field(default_factory=list)


@dataclass(frozen=True, kw_only=True, slots=True)
class ClassifiedTreeVo:
    name: str
    is_dir: bool
    path_display: str
    passport: ComponentPassport
    children: List["ClassifiedTreeVo"] = field(default_factory=list)


@dataclass(frozen=True)
class ScanResult:
    """Aggregate result of a project scan."""
    graph: "DependencyGraph" 
    source_tree: Dict[str, Any]