import logging
from collections.abc import Generator
from collections.abc import Set as AbstractSet
from dataclasses import dataclass
from pathlib import Path

from dddguard.shared.domain import ScannerConfig

from ....app import IProjectReader
from ....domain import SourceFileVo

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class FileSystemRepository(IProjectReader):
    """
    Driven Port Implementation: File System Adapter.

    Responsible for:
    1. Traversing the directory tree (OS I/O).
    2. Applying 'Ignore' rules defined in Config (Filtering).
    3. Safe reading of text content (UTF-8).
    4. capturing I/O errors and returning them as part of the domain object
       (instead of raising exceptions and breaking the scan flow).
    """

    def read_project(
        self,
        scanner_config: ScannerConfig,
        target_path: Path,
        scan_all: bool = False,
    ) -> Generator[SourceFileVo, None, None]:
        """
        Streams files from the disk one by one (Generator).

        Logic Flow:
        1. Checks if target_path is a single file.
        2. If dir, loads exclusion rules from Config.
        3. Walks the tree recursively.
        4. Filters out ignored files/extensions/sizes.
        5. Attempts to read content.

        Error Handling:
        If a file passes the filters but fails to read (e.g. Permission denied,
        Bad Encoding), it YIELDS a SourceFileVo with `reading_error` set.
        It does NOT raise exception.

        Args:
            root_path: Entry point for scanning.
            scan_all: Strategy flag.
                      False -> Strict Python scan (.py only).
                      True -> All text files (excluding explicit binary exts).

        Yields:
            SourceFileVo: Container with path, content (if success) or error (if failed).
        """
        # 1. Handle Single File case
        if target_path.is_file():
            # We explicitly allow the single file even if it doesn't match extension filters
            # logic: if user pointed to a specific file, they want it scanned.
            yield self._read_file_safe(target_path)
            return

        # 2. Prepare Filters (Optimization: load once)
        exclude_dirs = scanner_config.exclude_dirs
        ignore_files = scanner_config.ignore_files
        binary_exts = scanner_config.binary_extensions
        max_size = scanner_config.max_file_size_bytes

        # 3. Recursive Traversal
        for file_path in self._walk_pathlib(target_path, exclude_dirs):
            # A. Filter: Ignored Filenames (Exact match)
            if file_path.name in ignore_files:
                continue

            # B. Filter: Extension Strategy
            # If scan_all=False, we strictly require .py
            if not scan_all and file_path.suffix != ".py":
                continue

            # If scan_all=True, we strictly exclude known binaries
            if scan_all and file_path.suffix.lower() in binary_exts:
                continue

            # C. Filter: File Size (Performance guard)
            try:
                # stat() creates a system call, can raise OSError
                if file_path.stat().st_size > max_size and file_path.suffix != ".py":
                    continue
            except OSError:
                # If we can't even check size/existence, we likely can't read it.
                # Yield as an error to notify the user.
                yield SourceFileVo(path=file_path, reading_error="Access Denied (stat failed)")
                continue

            # D. Attempt Read
            # _read_file_safe handles the try/catch logic internally
            yield self._read_file_safe(file_path)

    def read_file(self, file_path: Path) -> SourceFileVo | None:
        """
        Reads a specific single file by path.
        Returns SourceFileVo even if reading failed (check .reading_error).
        Returns None only if file does not exist.
        """
        if not file_path.exists():
            return None
        return self._read_file_safe(file_path)

    def get_subdirectories(self, path: Path, scanner_config: ScannerConfig) -> list[Path]:
        """
        Utility for CLI autocompletion or partial scanning.
        Returns immediate subdirectories, respecting exclude config.
        """
        exclude_dirs = scanner_config.exclude_dirs
        results = []
        try:
            if not path.exists() or not path.is_dir():
                return []

            for entry in path.iterdir():
                if not entry.is_dir():
                    continue
                if entry.name in exclude_dirs or entry.name.startswith("."):
                    continue
                results.append(entry)
        except OSError as e:
            logger.warning("Cannot list directory '%s': %s", path, e)
        return sorted(results)

    def _walk_pathlib(
        self, path: Path, exclude_dirs: AbstractSet[str]
    ) -> Generator[Path, None, None]:
        """
        Custom recursive generator using pathlib.iterdir().
        """
        try:
            for entry in path.iterdir():
                # Prune hidden dirs and excluded dirs immediately
                if entry.name in exclude_dirs or entry.name.startswith("."):
                    continue

                if entry.is_dir():
                    yield from self._walk_pathlib(entry, exclude_dirs)
                elif entry.is_file():
                    yield entry
        except (PermissionError, OSError) as e:
            logger.warning("Skipping unreadable directory '%s': %s", path, e)

    def _read_file_safe(self, path: Path) -> SourceFileVo:
        """
        Internal helper: Attempts to read file content as UTF-8.
        Wraps errors into the SourceFileVo instead of raising.
        """
        try:
            content = path.read_text(encoding="utf-8", errors="strict")
            return SourceFileVo(path=path, content=content)
        except UnicodeDecodeError:
            return SourceFileVo(path=path, content=None, reading_error="Binary or non-UTF8 content")
        except OSError as e:
            return SourceFileVo(path=path, content=None, reading_error=f"I/O Error: {e!s}")
