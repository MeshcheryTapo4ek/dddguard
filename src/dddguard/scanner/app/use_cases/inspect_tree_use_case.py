from dataclasses import dataclass
from pathlib import Path

from ..interfaces import IDetectionGateway, IClassificationGateway
from ...domain.value_objects import ClassifiedTreeVo


@dataclass(frozen=True, kw_only=True, slots=True)
class InspectTreeUseCase:
    """
    Macro UseCase: Scans a directory structure and applies classification 
    to every node for visualization purposes.
    """

    detection_gateway: IDetectionGateway
    classification_gateway: IClassificationGateway

    def execute(self, target_path: Path, exclude_dirs: list[str]) -> ClassifiedTreeVo:
        return self._build_node_recursive(target_path, target_path, set(exclude_dirs))

    def _build_node_recursive(
        self, current_path: Path, root: Path, exclude_dirs: set[str]
    ) -> ClassifiedTreeVo:
        
        # 1. Identify current node (Real logic via Gateway)
        passport = self.classification_gateway.identify_component(current_path)
        
        # 2. Recurse if directory
        children = []
        if current_path.is_dir():
            try:
                for entry in sorted(current_path.iterdir(), key=lambda e: (not e.is_dir(), e.name)):
                    if entry.name in exclude_dirs or entry.name.startswith("."):
                        continue
                    # Skip __pycache__ specifically just in case
                    if entry.name == "__pycache__":
                        continue
                        
                    children.append(self._build_node_recursive(entry, root, exclude_dirs))
            except PermissionError:
                pass

        return ClassifiedTreeVo(
            name=current_path.name,
            is_dir=current_path.is_dir(),
            path_display=str(current_path.relative_to(root.parent)) if root.parent != root else str(current_path),
            passport=passport,
            children=children
        )