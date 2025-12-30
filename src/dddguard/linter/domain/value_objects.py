from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True, kw_only=True, slots=True)
class ScannedImportVo:
    """Internal representation of a dependency link."""

    target_module: str
    target_context: Optional[str]
    target_layer: Optional[str]


@dataclass(frozen=True, kw_only=True, slots=True)
class ScannedNodeVo:
    """Internal representation of a code module."""

    module_path: str
    context: str
    layer: str
    imports: List[ScannedImportVo] = field(default_factory=list)


@dataclass(frozen=True, kw_only=True, slots=True)
class ViolationVo:
    """Represents a single architectural violation."""

    rule_id: str
    severity: str
    message: str
    source_module: str
    source_layer: str
    target_module: str
    target_layer: str
    target_context: str


@dataclass(frozen=True, kw_only=True, slots=True)
class LinterReportVo:
    total_files_scanned: int
    violations: List[ViolationVo] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(v.severity == "error" for v in self.violations)
