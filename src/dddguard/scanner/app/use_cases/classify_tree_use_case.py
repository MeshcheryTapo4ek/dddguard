from dataclasses import dataclass
from pathlib import Path

from ...domain import SrmEngineService, ClassifiedTreeVo


@dataclass(frozen=True, kw_only=True, slots=True)
class ClassifyTreeUseCase:
    """
    App Service: Traverses directory and generates domain trees.
    Returns PURE Domain objects.
    """

    srm_engine: SrmEngineService

    def execute(self, root_path: Path, exclude_dirs: set[str]) -> ClassifiedTreeVo:
        return self._build_node(root_path, root_path, exclude_dirs)

    def _build_node(
        self, current_path: Path, project_root: Path, exclude_dirs: set[str]
    ) -> ClassifiedTreeVo:
        rel_path = current_path.relative_to(project_root)
        parts = rel_path.parts if rel_path.parts else (".",)
        passport = self.srm_engine.identify(parts, current_path.stem)

        children = []
        if current_path.is_dir():
            try:
                for entry in sorted(
                    current_path.iterdir(), key=lambda e: (not e.is_dir(), e.name)
                ):
                    if entry.name in exclude_dirs or entry.name.startswith("."):
                        continue
                    children.append(self._build_node(entry, project_root, exclude_dirs))
            except PermissionError:
                pass

        return ClassifiedTreeVo(
            name=current_path.name,
            is_dir=current_path.is_dir(),
            path_display=str(rel_path),
            passport=passport,
            children=children,
        )
