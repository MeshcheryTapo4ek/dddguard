from dataclasses import dataclass
from pathlib import Path


@dataclass
class ScanOptions:
    """
    Mutable configuration state for the Scan Wizard.
    Acts as a DTO between the Wizard (TUI) and the Facade.
    """

    target_path: Path

    # Execution Flags
    scan_all: bool = False

    # Presentation Flags (Handled by CLI adapter, not Domain)
    file_tree_only: bool = False  # If True, suppresses file content in JSON output

    # Scope Toggles
    include_assets: bool = True

    # Filters
    # If None, implies "All Allowed"
    macro_contexts: list[str] | None = None
    contexts: list[str] | None = None
    layers: list[str] | None = None

    import_depth: int = 0

    # Output
    output_json: Path = Path("project_tree.json")
