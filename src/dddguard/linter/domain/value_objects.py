from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True, kw_only=True, slots=True)
class ViolationVo:
    """Represents a single architectural violation found during analysis."""
    rule_id: str  # e.g. "R100", "C200"
    severity: str  # "error", "warning"
    message: str

    source_module: str
    source_layer: str

    target_module: str
    target_layer: str
    target_context: str


@dataclass(frozen=True, kw_only=True, slots=True)
class LinterReportVo:
    """Aggregated report of the linting process."""
    total_files_scanned: int
    violations: List[ViolationVo] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(v.severity == "error" for v in self.violations)