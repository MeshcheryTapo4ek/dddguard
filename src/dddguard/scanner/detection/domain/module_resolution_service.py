from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True, kw_only=True)
class ModuleResolutionService:
    """
    Domain Service: Resolves logical Python module paths to physical file paths (and vice-versa).
    Pure logic, IO-agnostic (except for checking existence via Path object).
    """

    @staticmethod
    def calculate_logical_path(file_path: Path, source_dir: Path) -> str | None:
        """
        Reverse resolution: '/.../src/foo/bar.py' -> 'foo.bar'.
        Returns None if file is not relative to source_dir.
        """
        try:
            rel = file_path.relative_to(source_dir)
            # Efficiently strip suffix and handle parts
            parts = list(rel.with_suffix("").parts)

            # Handle package convention (strip __init__)
            if parts and parts[-1] == "__init__":
                parts.pop()

            return ".".join(parts)
        except ValueError:
            return None
