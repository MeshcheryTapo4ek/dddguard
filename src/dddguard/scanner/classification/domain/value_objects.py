from dataclasses import dataclass, field
from functools import cached_property
from typing import List, Dict

from dddguard.shared.domain import (
    ComponentPassport,
    ArchetypeType
)


@dataclass(frozen=True, kw_only=True, slots=True)
class EnrichedNodeVo:
    """
    A Graph Node enriched with architectural metadata.
    """
    module_path: str
    passport: ComponentPassport
    imports: List[str] = field(default_factory=list)

    @property
    def is_architecturally_valid(self) -> bool:
        return self.passport.component_type != ArchetypeType.UNKNOWN


@dataclass(frozen=True, kw_only=True)
class ClassificationStatsVo:
    """
    Metrics regarding the identification process.
    Uses cached_property for lazy, once-only calculation.
    """
    total_nodes: int
    classified_nodes: int
    unknown_nodes: int
    
    @cached_property
    def coverage_percent(self) -> float:
        if self.total_nodes == 0:
            return 0.0
        return round((self.classified_nodes / self.total_nodes) * 100, 2)


@dataclass(frozen=True, kw_only=True, slots=True)
class EnrichedGraph:
    nodes: Dict[str, EnrichedNodeVo] = field(default_factory=dict)
    stats: ClassificationStatsVo