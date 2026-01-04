from dataclasses import dataclass, field
from typing import Dict, Any, List

from dddguard.shared.domain import ComponentPassport


@dataclass(frozen=True, kw_only=True, slots=True)
class ScanResponseSchema:
    """
    Macro Response: The final consolidated report of the scanning process.
    Aggregates data from Detection (Physical) and Classification (Logical).
    """

    # From Detection Context (Physical Tree)
    source_tree: Dict[str, Any]
    
    # From Classification Context (Enriched Graph)
    # Format: { "module.path": { "passport": {...}, "imports": [...] } }
    dependency_graph: Dict[str, Any]
    
    # Aggregated Stats
    context_count: int
    file_count: int              # Total physical files
    snapshot_file_count: int     # Files visible in graph (filtered)
    unclassified_count: int      # Files with UNKNOWN type
    
    total_lines_of_code: int = 0
    success: bool = True
    error_message: str | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class ClassifiedNodeSchema:
    """
    Recursive Tree Node for the 'classifydir' visualization command.
    """
    name: str
    is_dir: bool
    path_display: str  # Relative path string for UI
    passport: ComponentPassport
    children: List["ClassifiedNodeSchema"] = field(default_factory=list)