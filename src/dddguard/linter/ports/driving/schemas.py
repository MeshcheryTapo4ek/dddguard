from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True, kw_only=True, slots=True)
class ViolationSchema:
    """
    Driving Schema: Represents a single rule violation for presentation.
    """

    rule_id: str
    message: str
    source: str
    target: str
    severity: str
    target_context: Optional[str] = None


@dataclass(frozen=True, kw_only=True, slots=True)
class LinterResponseSchema:
    """
    Driving Schema: The final report of a linting run.
    """

    total_scanned: int
    violations: List[ViolationSchema] = field(default_factory=list)
    success: bool = True
