from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class ScanOptions:
    """
    Mutable configuration state for the Scan Wizard.
    Used strictly within the Console Adapter to accumulate user choices.
    """

    target_path: Path

    # Flags
    dirs_only: bool = False
    scan_all: bool = False

    # Filters
    contexts: Optional[List[str]] = None
    layers: Optional[List[str]] = None  # None means ALL layers
    
    # Advanced
    import_depth: int = 0

    # Output
    output_json: Path = Path("project_tree.json")