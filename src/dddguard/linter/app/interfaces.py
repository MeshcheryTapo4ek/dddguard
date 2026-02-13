from pathlib import Path
from typing import Protocol

from dddguard.shared.domain import CodeGraph


class IScannerGateway(Protocol):
    """
    Application Port: Abstract interface for retrieving project structure.
    """

    def get_project_graph(self, root_path: Path) -> CodeGraph: ...
