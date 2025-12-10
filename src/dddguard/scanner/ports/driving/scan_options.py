from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

@dataclass
class ScanOptions:
    """
    Holds the mutable configuration state for the Scan Wizard.
    """
    target_path: Path
    
    # Flags
    verbose: bool = False
    dirs_only: bool = False
    scan_all: bool = False
    
    # Scope Visibility Flags (New)
    show_root: bool = True
    show_shared: bool = True
    
    # Filters
    contexts: Optional[List[str]] = None
    layers: Optional[List[str]] = None # None means ALL layers
    
    # Output
    output_json: Path = Path("project_tree.json")