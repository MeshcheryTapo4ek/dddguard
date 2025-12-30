from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, kw_only=True, slots=True)
class ScaffolderFileVo:
    """
    Domain representation of a file to be written.
    """

    path: Path
    content: str
