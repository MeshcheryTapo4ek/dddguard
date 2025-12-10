from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any


@dataclass(frozen=True, kw_only=True, slots=True)
class RenderedFileVo:
    """A file ready to be written to disk."""
    relative_path: Path
    content: str


@dataclass(frozen=True, kw_only=True, slots=True)
class TemplateDefinition:
    """
    Represents a raw template loaded from the filesystem.
    """
    id: str
    category: str
    description: str
    dependencies: List[str] = field(default_factory=list)
    files: Dict[str, str] = field(default_factory=dict)
    # New: Extra variables from manifest (e.g. "root_package": "my_ctx")
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, kw_only=True, slots=True)
class CategoryDefinition:
    """Metadata for a group of templates."""
    id: str
    title: str
    description: str