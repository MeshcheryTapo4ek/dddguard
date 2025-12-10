from typing import Protocol, List
from pathlib import Path

from ..domain import ContextTower


class IDiagramRenderer(Protocol):
    def render(self, towers: List[ContextTower], output_path: Path) -> None: ...