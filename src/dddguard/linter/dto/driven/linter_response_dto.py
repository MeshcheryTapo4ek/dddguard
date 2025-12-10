from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True, kw_only=True, slots=True)
class ViolationDto:
    rule_id: str
    message: str
    source: str
    target: str
    severity: str
    target_context: Optional[str] = None 


@dataclass(frozen=True, kw_only=True, slots=True)
class LinterResponseDto:
    total_scanned: int
    violations: List[ViolationDto] = field(default_factory=list)
    success: bool = True