from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional

from dddguard.shared.domain import (
    LayerEnum,
    ComponentType,
    ScopeEnum,
)
from .value_objects import DependencyLink, ScannedModuleVo


@dataclass(kw_only=True)
class DependencyNode:
    """
    Graph Node Entity.
    Identity: module_path.
    State: is_visible (Mutated during filtering/expansion phases).
    """

    module_path: str
    context: str
    layer: LayerEnum
    component_type: ComponentType
    scope: ScopeEnum
    imports: List[DependencyLink] = field(default_factory=list)
    
    # Mutable State
    is_visible: bool = False
    
    # Traversal State (Transatile)
    # Tracks the maximum 'import depth budget' reaching this node.
    remaining_depth: int = -1

    @property
    def is_external(self) -> bool:
        return self.context == "external" or self.context is None


@dataclass
class DependencyGraph:
    """
    Aggregate Root for the Architecture Graph.
    Encapsulates traversal and export logic.
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
        """Returns only nodes marked as visible."""
        return [n for n in self.nodes.values() if n.is_visible]

    def to_hierarchical_dict(self) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """
        Exports the graph to a format suitable for the UI Adapter/Schema.
        Only includes visible nodes.
        """
        output: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
        
        for node in self.visible_nodes:
            if node.context not in output:
                output[node.context] = {}

            layer_val = str(node.layer)
            if layer_val not in output[node.context]:
                output[node.context][layer_val] = []

            node_data = {
                "module": node.module_path,
                "type": str(node.component_type),
                "imports": [
                    {
                        "module": imp.target_module,
                        "context": imp.target_context,
                        "layer": imp.target_layer,
                        "type": imp.target_type,
                    }
                    for imp in node.imports
                ],
            }
            output[node.context][layer_val].append(node_data)
        return output


@dataclass
class ProjectStructureTree:
    """
    Entity responsible for building the visual directory structure (Source Tree).
    Encapsulates the nested dictionary construction logic.
    """
    
    _root_dict: Dict[str, Any] = field(default_factory=dict)

    def add_module(
        self, 
        module: ScannedModuleVo, 
        project_root: Path, 
        dirs_only: bool
    ) -> None:
        """
        Adds a ScannedModule (file) to the tree structure.
        Implicitly creates parent directories.
        """
        self._add_path_recursive(
            current_dict=self._root_dict,
            path=module.file_path,
            root=project_root,
            content=module.content,
            dirs_only=dirs_only
        )

    def to_dict(self) -> Dict[str, Any]:
        return self._root_dict

    def _add_path_recursive(
        self,
        current_dict: Dict[str, Any],
        path: Path,
        root: Path,
        content: str,
        dirs_only: bool,
    ) -> None:
        try:
            rel = path.relative_to(root)
            cursor = current_dict
            
            # Navigate/Create directories
            for part in rel.parts[:-1]:
                cursor = cursor.setdefault(part, {})
            
            # Add file leaf (unless directory exists with same name, which is rare in valid OS)
            # Logic: If dirs_only is True, we mask content.
            value = "<Dir>" if dirs_only else content
            
            # Don't overwrite if it's a directory we've already traversed as a package
            # or if it exists. Simple set is enough.
            cursor[rel.parts[-1]] = value
            
        except ValueError:
            pass