from dataclasses import dataclass, field
from typing import Dict, Any, List
from dddguard.shared.domain import ComponentPassport
from ..classification.domain import EnrichedNodeVo

@dataclass(frozen=True, kw_only=True, slots=True)
class DetectionResultVo:
    """
    Domain representation of the physical scan result.
    Decouples App layer from Detection Context Schemas.
    """
    graph_nodes: Dict[str, Any]  # Raw nodes still use dicts as they are untyped at this stage
    source_tree: Dict[str, Any]
    stats: Dict[str, int]


@dataclass(frozen=True, kw_only=True, slots=True)
class ClassificationResultVo:
    """
    Domain representation of the logical classification result.
    NOW STRICTLY TYPED: No more Dict[str, Any].
    """
    nodes: Dict[str, EnrichedNodeVo] 
    unknown_count: int


@dataclass(frozen=True, kw_only=True, slots=True)
class ScanReportVo:
    """
    Aggregate result of the Scanner process.
    """
    source_tree: Dict[str, Any]
    dependency_graph: Dict[str, Any] # Kept flexible for JSON serialization, but populated by strict objects
    
    # Stats
    context_count: int
    file_count: int
    snapshot_file_count: int
    unclassified_count: int
    
    total_lines_of_code: int = 0
    success: bool = True
    error_message: str | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class ClassifiedTreeVo:
    """
    Recursive tree structure for visualization.
    """
    name: str
    is_dir: bool
    path_display: str
    passport: ComponentPassport
    children: List["ClassifiedTreeVo"] = field(default_factory=list)