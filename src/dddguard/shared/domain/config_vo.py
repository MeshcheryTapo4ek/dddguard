from dataclasses import dataclass, field
from typing import Set, List, Optional
from pathlib import Path

from .rules import ClassificationRule


@dataclass(frozen=True, slots=True, kw_only=True)
class ScannerConfig:
    """
    Configuration specific to the scanning process.
    """
    exclude_dirs: Set[str] = field(default_factory=lambda: {
        ".git", ".venv", "venv", "__pycache__", "node_modules", 
        ".idea", ".vscode", "migrations", "build", "dist", "coverage", ".mypy_cache"
    })
    
    ignore_files: Set[str] = field(default_factory=lambda: {
        "conftest.py", "manage.py", "setup.py", "package-lock.json", "yarn.lock"
    })
    
    # Files larger than this (in bytes) will be skipped in '--all' mode. 
    # Default: 500 KB 
    max_file_size_bytes: int = 500 * 1024 

    # Extensions to strictly ignore in '--all' mode (Media, Binary, Archives).
    binary_extensions: Set[str] = field(default_factory=lambda: {
        # Images
        ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".bmp", ".tiff", ".webp",
        # Audio/Video
        ".mp3", ".wav", ".mp4", ".mov", ".avi", ".flac",
        # Documents/Archives
        ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".zip", ".tar", ".gz", ".7z", ".rar",
        # Compiled/Binary
        ".exe", ".dll", ".so", ".dylib", ".bin", ".pyc", ".class", ".jar", ".db", ".sqlite"
    })

    # Custom rules loaded from YAML
    custom_rules: List[ClassificationRule] = field(default_factory=list)


@dataclass(frozen=True, slots=True, kw_only=True)
class ProjectConfig:
    """
    General project settings.
    """
    source_dir: str = "src"
    tests_dir: str = "tests"
    docs_dir: str = "docs"
    
    project_root: Path = field(default_factory=Path.cwd)
    
    # Track where this config came from (None if using defaults/CLI args only)
    config_file_path: Optional[Path] = None 

    @property
    def absolute_source_path(self) -> Path:
        src = Path(self.source_dir)
        if src.is_absolute():
            return src
        return (self.project_root / src).resolve()

    @property
    def has_config_file(self) -> bool:
        """Returns True if this config was loaded from a physical file."""
        return self.config_file_path is not None


@dataclass(frozen=True, slots=True, kw_only=True)
class ConfigVo:
    """
    Global Configuration Aggregate.
    """
    project: ProjectConfig = field(default_factory=ProjectConfig)
    scanner: ScannerConfig = field(default_factory=ScannerConfig)