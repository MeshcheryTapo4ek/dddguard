from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .value_objects import (
    DependencyLink,
    ScanStatisticsVo
)


@dataclass(kw_only=True)
class DependencyNode:
    """
    Raw Graph Node.
    Identity: module_path (logical python path).
    """
    module_path: str
    imports: List[DependencyLink] = field(default_factory=list)
    
    # Traversal / filtering state
    is_visible: bool = False
    remaining_depth: int = -1


@dataclass
class DependencyGraph:
    """
    Raw Dependency Graph.
    Contains only modules and their physical imports.
    """
    nodes: Dict[str, DependencyNode] = field(default_factory=dict)

    def add_node(self, node: DependencyNode) -> None:
        self.nodes[node.module_path] = node

    def get_node(self, module_path: str) -> Optional[DependencyNode]:
        return self.nodes.get(module_path)

    @property
    def all_nodes(self) -> List[DependencyNode]:
        return list(self.nodes.values())

    @property
    def visible_nodes(self) -> List[DependencyNode]:
        return [n for n in self.nodes.values() if n.is_visible]

    def compute_statistics(self) -> ScanStatisticsVo:
        """Physical metrics calculation."""
        visible = self.visible_nodes
        relations = sum(len(n.imports) for n in visible)

        return ScanStatisticsVo(
            total_files=len(self.nodes), # assuming 1 module = 1 file usually
            total_modules=len(visible),
            total_relations=relations
        )
    
@dataclass
class ProjectStructureTree:
    """
    Entity responsible for building the visual directory structure (Source Tree).
    """
    
    _root_dict: Dict = field(default_factory=dict)

    def add_module(self, module, scan_root, dirs_only) -> None:
        self._add_path_recursive(
            current_dict=self._root_dict,
            path=module.file_path,
            root=scan_root,
            content=module.content,
            dirs_only=dirs_only
        )

    def to_dict(self) -> Dict:
        return self._root_dict

    def _add_path_recursive(
        self,
        current_dict: Dict,
        path,
        root,
        content: str,
        dirs_only: bool,
    ) -> None:
        try:
            rel = path.relative_to(root)
            cursor = current_dict
            
            # Navigate/Create directories
            for part in rel.parts[:-1]:
                cursor = cursor.setdefault(part, {})
            
            # Add file leaf
            value = "<Dir>" if dirs_only else content
            cursor[rel.parts[-1]] = value
            
        except ValueError:
            pass