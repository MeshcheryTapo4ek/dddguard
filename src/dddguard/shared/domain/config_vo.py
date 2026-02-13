from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True, slots=True, kw_only=True)
class ScannerConfig:
    """
    Configuration specific to the scanning process.

    All collection fields use FrozenSet to guarantee true immutability
    (the dataclass is frozen, so references can't change; FrozenSet ensures
    the contents can't be mutated either).
    """

    exclude_dirs: frozenset[str] = field(
        default_factory=lambda: frozenset(
            {
                ".git",
                ".venv",
                "venv",
                "__pycache__",
                "node_modules",
                ".idea",
                ".vscode",
                "migrations",
                "build",
                "dist",
                "coverage",
                ".mypy_cache",
            }
        )
    )

    ignore_files: frozenset[str] = field(
        default_factory=lambda: frozenset(
            {
                "conftest.py",
                "manage.py",
                "setup.py",
                "package-lock.json",
                "yarn.lock",
            }
        )
    )

    # Files larger than this (in bytes) will be skipped in '--all' mode.
    # Default: 500 KB
    max_file_size_bytes: int = 500 * 1024

    # Extensions to strictly ignore in '--all' mode (Media, Binary, Archives).
    binary_extensions: frozenset[str] = field(
        default_factory=lambda: frozenset(
            {
                # Images
                ".png",
                ".jpg",
                ".jpeg",
                ".gif",
                ".ico",
                ".svg",
                ".bmp",
                ".tiff",
                ".webp",
                # Audio/Video
                ".mp3",
                ".wav",
                ".mp4",
                ".mov",
                ".avi",
                ".flac",
                # Documents/Archives
                ".pdf",
                ".doc",
                ".docx",
                ".xls",
                ".xlsx",
                ".zip",
                ".tar",
                ".gz",
                ".7z",
                ".rar",
                # Compiled/Binary
                ".exe",
                ".dll",
                ".so",
                ".dylib",
                ".bin",
                ".pyc",
                ".class",
                ".jar",
                ".db",
                ".sqlite",
            }
        )
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class ProjectConfig:
    """
    General project settings.
    All paths are Optional to detect 'unconfigured' state.
    """

    source_dir: str | None = None
    tests_dir: str | None = None
    docs_dir: str | None = None

    project_root: Path | None = None
    config_file_path: Path | None = None

    @property
    def absolute_source_path(self) -> Path | None:
        """
        Calculates absolute path only if both root and source_dir exist.
        Otherwise returns None, signaling an unconfigured state.
        """
        if not self.project_root or not self.source_dir:
            return None

        src = Path(self.source_dir)
        if src.is_absolute():
            return src
        return (self.project_root / src).resolve()


@dataclass(frozen=True, slots=True, kw_only=True)
class ConfigVo:
    """
    Global Configuration Aggregate.
    """

    project: ProjectConfig = field(default_factory=ProjectConfig)
    scanner: ScannerConfig = field(default_factory=ScannerConfig)
