from dataclasses import dataclass, field
from typing import Literal

from dddguard.shared.domain import (
    InternalAccessMatrix,
    LayerDirectionKey,
    RuleName,
)

# Severity levels used across linter domain and presentation
Severity = Literal["error", "warning", "info"]


@dataclass(frozen=True, kw_only=True, slots=True)
class ViolationSchema:
    """
    Driving Schema: Represents a single rule violation for presentation.
    """

    rule_name: RuleName
    message: str
    source: str
    target: str
    severity: Severity
    target_context: str | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class LinterResponseSchema:
    """
    Driving Schema: The final report of a linting run.
    """

    total_scanned: int
    violations: tuple[ViolationSchema, ...] = field(default_factory=tuple)
    success: bool = True


@dataclass(frozen=True, kw_only=True, slots=True)
class FractalRulesSchema:
    """Fractal (Parent <-> Child) access rules."""

    upstream_allowed: frozenset[LayerDirectionKey]
    upstream_forbidden: frozenset[LayerDirectionKey]
    downstream_allowed: frozenset[LayerDirectionKey]
    downstream_forbidden: frozenset[LayerDirectionKey]


@dataclass(frozen=True, kw_only=True, slots=True)
class RulesMatrixSchema:
    """
    Driving Schema: Typed container for all 13 architectural rules.
    Covers Internal (1-7), Fractal (8-9), Cross-Context (10-11), Scope (12-13).
    """

    # Group 1: Internal Rules
    internal: InternalAccessMatrix

    # Group 2: Fractal Rules
    fractal: FractalRulesSchema

    # Group 3: Cross-Context Rules
    outbound_allowed: frozenset[LayerDirectionKey]
    inbound_allowed: frozenset[LayerDirectionKey]
