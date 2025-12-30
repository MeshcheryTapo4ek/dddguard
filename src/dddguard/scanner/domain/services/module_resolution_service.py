from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True, slots=True, kw_only=True)
class ModuleResolutionService:
    """
    Domain Service: Resolves logical Python module paths to physical file paths.
    Does not perform I/O beyond checking path existence.
    """

    def resolve_module_path(
        self, module_dot_path: str, source_root: Path
    ) -> Optional[Path]:
        """
        Converts 'dddguard.shared' -> '/.../src/dddguard/shared/__init__.py'
        or 'dddguard.utils' -> '/.../src/dddguard/utils.py'
        """
        if not module_dot_path:
            return None

        # Convert dots to slashes
        rel_path = module_dot_path.replace(".", "/")
        base_path = source_root / rel_path

        # 1. Check for package (__init__.py)
        package_path = base_path / "__init__.py"
        if package_path.exists():
            return package_path

        # 2. Check for module (.py)
        module_path = base_path.with_suffix(".py")
        if module_path.exists():
            return module_path

        return None

    def calculate_logical_path(self, file_path: Path, source_root: Path) -> Optional[str]:
        """
        Reverse resolution: '/.../src/foo/bar/__init__.py' -> 'foo.bar'
        Returns None if file is not relative to source_root.
        """
        try:
            rel = file_path.relative_to(source_root)
            parts = list(rel.with_suffix("").parts)
            # Handle package convention
            if parts and parts[-1] == "__init__":
                parts.pop()
            return ".".join(parts)
        except ValueError:
            return None