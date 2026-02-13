from dataclasses import dataclass, field
from typing import Literal

from dddguard.shared.domain import RuleName

# Severity levels for domain events
Severity = Literal["error", "warning", "info"]


@dataclass(frozen=True, kw_only=True, slots=True)
class ViolationEvent:
    """Represents a single architectural violation."""

    rule_name: RuleName
    severity: Severity
    message: str
    source_module: str
    source_layer: str
    target_module: str
    target_layer: str
    target_context: str


@dataclass(frozen=True, kw_only=True, slots=True)
class LinterReport:
    """Immutable report of a linting run."""

    total_files_scanned: int
    violations: tuple[ViolationEvent, ...] = field(default_factory=tuple)

    @property
    def has_errors(self) -> bool:
        return any(v.severity == "error" for v in self.violations)
