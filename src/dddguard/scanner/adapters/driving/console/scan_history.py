import json
from pathlib import Path
from typing import Optional

from .scan_options import ScanOptions


# Define a temporary file path for storing the last scan options
# This should ideally be in a user-specific config directory, but for simplicity,
# we'll use a known location within the project or a temp folder.
# For now, let's assume a .dddguard_cache in the project root.
_LAST_SCAN_FILE = Path(".dddguard_cache") / "last_scan_options.json"


def save_last_scan_options(options: ScanOptions) -> None:
    """
    Saves the given ScanOptions object to a JSON file.
    """
    _LAST_SCAN_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(_LAST_SCAN_FILE, "w", encoding="utf-8") as f:
        # We need to convert Path objects to strings for JSON serialization
        serializable_options = options.__dict__.copy()
        serializable_options["target_path"] = str(options.target_path)
        serializable_options["output_json"] = str(options.output_json)
        
        # Convert List[str] | None to List[str] or None to handle default empty lists correctly
        serializable_options["contexts"] = options.contexts if options.contexts is not None else None
        serializable_options["layers"] = options.layers if options.layers is not None else None

        json.dump(serializable_options, f, indent=2)


def load_last_scan_options() -> Optional[ScanOptions]:
    """
    Loads the last saved ScanOptions object from a JSON file.
    Returns None if the file does not exist or cannot be parsed.
    """
    if not _LAST_SCAN_FILE.exists():
        return None

    try:
        with open(_LAST_SCAN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            
            # Convert string paths back to Path objects
            if "target_path" in data:
                data["target_path"] = Path(data["target_path"])
            if "output_json" in data:
                data["output_json"] = Path(data["output_json"])
            
            # Ensure lists are lists, not None, for constructor
            if data.get("contexts") is None:
                data["contexts"] = None
            if data.get("layers") is None:
                data["layers"] = None

            # Create and return ScanOptions instance
            return ScanOptions(**data)
    except (json.JSONDecodeError, FileNotFoundError, TypeError) as e:
        # Log the error if necessary
        print(f"Warning: Could not load last scan options. Error: {e}")
        return None

