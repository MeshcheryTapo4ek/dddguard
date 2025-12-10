from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, List, Dict, Optional, Set

from dddguard.shared import (
    ProjectBoundedContextNames,
    ContextLayerEnum,
    AnyComponentType,
)


@dataclass(frozen=True, kw_only=True, slots=True)
class SourceFileVo:
    path: Path
    content: str


@dataclass(frozen=True, kw_only=True, slots=True)
class ClassificationResultVo:
    scope: ProjectBoundedContextNames
    layer: ContextLayerEnum
    component_type: AnyComponentType
    context_name: str
    is_definitive: bool = False


@dataclass(frozen=True, kw_only=True, slots=True)
class ImportedModuleVo:
    """
    Represents a raw import statement extracted from AST.
    """
    module_path: str
    lineno: int
    is_relative: bool
    # Stores imported names list (e.g., ['ScanProjectUseCase'])
    imported_names: List[str] = field(default_factory=list)


# --- Graph Domain Objects ---

@dataclass(frozen=True, kw_only=True, slots=True)
class DependencyLink:
    source_module: str
    target_module: str
    target_context: Optional[str] = None
    target_layer: Optional[str] = None
    target_type: Optional[str] = None


@dataclass(frozen=True, kw_only=True, slots=True)
class DependencyNode:
    module_path: str
    context: str
    layer: ContextLayerEnum
    component_type: AnyComponentType
    scope: ProjectBoundedContextNames
    imports: List[DependencyLink] = field(default_factory=list)

    @property
    def is_external(self) -> bool:
        return self.context == "external" or self.context is None


@dataclass(frozen=True, kw_only=True, slots=True)
class DependencyGraph:
    nodes: Dict[str, DependencyNode] = field(default_factory=dict)

    @property
    def all_nodes(self) -> List[DependencyNode]:
        return list(self.nodes.values())

    def get_node(self, module_path: str) -> Optional[DependencyNode]:
        return self.nodes.get(module_path)

    def filter_by_contexts(self, allowed_contexts: Set[str]) -> "DependencyGraph":
        """
        Creates a new DependencyGraph containing nodes from the specified contexts
        AND their direct dependencies (neighbors).
        """
        if not allowed_contexts:
            return self

        # 1. Identify primary nodes (Roots of the view)
        primary_nodes = {
            path: node 
            for path, node in self.nodes.items()
            if node.context in allowed_contexts
        }
        
        # 2. Identify neighbors (Direct dependencies)
        neighbor_paths = set()
        for node in primary_nodes.values():
            for link in node.imports:
                neighbor_paths.add(link.target_module)

        # 3. Construct Final Set
        filtered_nodes = {}
        filtered_nodes.update(primary_nodes)

        for path in neighbor_paths:
            if path in self.nodes and path not in filtered_nodes:
                filtered_nodes[path] = self.nodes[path]

        return replace(self, nodes=filtered_nodes)

    def filter_by_layers(self, allowed_layers: Set[str]) -> "DependencyGraph":
        """
        Filters nodes based on their architectural layer.
        Strict filtering: Only nodes belonging to the specified layers are kept.
        """
        if not allowed_layers:
            return self

        # Normalize input to ensure matching against Enum values
        allowed = {l.lower() for l in allowed_layers}

        filtered_nodes = {}
        for path, node in self.nodes.items():
            # Get string value of Enum safely
            layer_val = node.layer.value if hasattr(node.layer, "value") else str(node.layer)
            
            if layer_val.lower() in allowed:
                filtered_nodes[path] = node
        
        return replace(self, nodes=filtered_nodes)

    def to_hierarchical_dict(self) -> Dict[str, Dict[str, List[Dict]]]:
        output = {}
        for node in self.nodes.values():
            if node.context not in output:
                output[node.context] = {}
            
            layer_val = node.layer.value if hasattr(node.layer, "value") else str(node.layer)
            if layer_val not in output[node.context]:
                output[node.context][layer_val] = []

            node_data = {
                "module": node.module_path,
                "type": node.component_type.value if hasattr(node.component_type, "value") else str(node.component_type),
                "imports": [
                    {
                        "module": imp.target_module,
                        "context": imp.target_context,
                        "layer": imp.target_layer,
                        "type": imp.target_type
                    }
                    for imp in node.imports
                ]
            }
            output[node.context][layer_val].append(node_data)
        return output
    

@dataclass(frozen=True)
class ScanResult:
    graph: DependencyGraph
    source_tree: Dict[str, Any]