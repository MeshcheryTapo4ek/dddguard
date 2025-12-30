from dataclasses import dataclass, field
from typing import Dict, Any, List

from dddguard.shared.domain import ComponentPassport


@dataclass(frozen=True, slots=True, kw_only=True)
class ScanResponseSchema:
    """
    Driving Schema: Contains only serializable data for Presentation Layer.
    Decouples CLI/API from Domain Entities.
    """

    source_tree: Dict[str, Any]
    dependency_graph: Dict[str, Any]
    
    # Stats
    context_count: int
    file_count: int             # Total files scanned/ingested
    snapshot_file_count: int    # Files actually included in output (Visible)
    unclassified_count: int     # Files that failed architectural classification
    
    total_lines_of_code: int = 0

    # Metadata for the report
    success: bool = True
    error_message: str | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class ClassifiedNodeSchema:
    """
    Data contract for a classified file system node including the full Passport.
    """

    name: str
    is_dir: bool
    path_display: str  # Full relative path for CLI display
    passport: ComponentPassport
    children: List["ClassifiedNodeSchema"] = field(default_factory=list)