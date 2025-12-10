from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True, slots=True)
class ScanResponseDto:
    """
    Driving DTO: Contains only serializable data for Presentation Layer.
    Decouples CLI from Domain Entities (Graph, ScanResult).
    """
    source_tree: Dict[str, Any]
    context_count: int
    file_count: int
    total_lines_of_code: int = 0
    
    # Metadata for the report
    success: bool = True
    error_message: str | None = None