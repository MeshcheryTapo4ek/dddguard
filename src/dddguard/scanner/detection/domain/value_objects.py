from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True, kw_only=True, slots=True)
class ImportedModuleVo:
    """
    Specific to Detection: Detail about a specific import statement line in AST.
    """

    module_path: str
    lineno: int
    is_relative: bool
    imported_names: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, kw_only=True, slots=True)
class ScannedModuleVo:
    """
    Intermediate VO holding AST parsing results before Graph construction.
    Acts as a temporary holder/DTO within the Use Case scope.
    """

    logical_path: str
    file_path: Path

    # Content is Optional for cases where file read failed or it is a binary asset
    content: str | None

    raw_imports: Sequence[ImportedModuleVo] = field(default_factory=tuple)

    @property
    def is_package(self) -> bool:
        return self.file_path.name == "__init__.py"


@dataclass(frozen=True, kw_only=True, slots=True)
class SourceFileVo:
    """
    Foundations: Physical file content representation.

    Can represent two states:
    1. Success: content is str, reading_error is None.
    2. Failure: content is None, reading_error contains the exception message.
    """

    path: Path
    content: str | None = None
    reading_error: str | None = None

    @property
    def is_readable(self) -> bool:
        return self.content is not None and self.reading_error is None
