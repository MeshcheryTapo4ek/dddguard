from typing import Protocol, List
from pathlib import Path

from ..domain import ScannedNodeVo


class IScannerGateway(Protocol):
    """
    Application Port: Abstract interface for retrieving project structure.
    Returns Linter-native Value Objects (ScannedNodeVo).
    """

    def get_project_nodes(self, root_path: Path) -> List[ScannedNodeVo]: ...
