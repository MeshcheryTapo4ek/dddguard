from dataclasses import dataclass
from typing import Dict, List

from dddguard.shared.domain import ComponentPassport

@dataclass(frozen=True, kw_only=True, slots=True)
class ClassifiedNodeSchema:
    """
    Public representation of a classified component.
    """
    module_path: str
    passport: ComponentPassport
    direct_dependencies: List[str]


@dataclass(frozen=True, kw_only=True, slots=True)
class ClassificationResponseSchema:
    """
    Root DTO containing the full architectural picture.
    """
    nodes: Dict[str, ClassifiedNodeSchema]
    coverage_percent: float
    total_components: int
    unknown_components: int