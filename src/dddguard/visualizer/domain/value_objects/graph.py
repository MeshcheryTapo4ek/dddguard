from dataclasses import dataclass, field
from typing import List, Dict, Optional


from dddguard.shared import ScopeEnum, LayerEnum, ComponentType


@dataclass(frozen=True, kw_only=True, slots=True)
class DependencyLink:
    """
    Visualizer's local representation of a connection between nodes.
    """

    source_module: str
    target_module: str
    target_context: Optional[str] = None
    target_layer: Optional[str] = None
    target_type: Optional[str] = None


@dataclass(frozen=True, kw_only=True, slots=True)
class DependencyNode:
    """
    Visualizer's local representation of a code component.
    """

    module_path: str
    context: str
    layer: LayerEnum
    component_type: ComponentType | str
    scope: ScopeEnum
    imports: List[DependencyLink] = field(default_factory=list)

    @property
    def is_external(self) -> bool:
        return self.context == "external" or self.context is None


@dataclass(frozen=True, kw_only=True, slots=True)
class DependencyGraph:
    """
    Visualizer's aggregate root for the graph structure.
    """

    nodes: Dict[str, DependencyNode] = field(default_factory=dict)

    @property
    def all_nodes(self) -> List[DependencyNode]:
        return list(self.nodes.values())
