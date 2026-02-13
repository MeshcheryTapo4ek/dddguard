from collections.abc import Iterator, Set
from dataclasses import dataclass, field
from typing import Union

from dddguard.shared.domain import CodeNode, LayerEnum


@dataclass(frozen=True, kw_only=True, slots=True)
class VisualElement:
    """
    Base value object for any element in the diagram (Node or Container).
    Position (x, y) is relative to its parent container.
    """

    x: float = 0.0
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0
    label: str = ""
    id: str = ""  # Unique identifier for edge linking
    color: str = "none"

    def walk_leaves(self) -> Iterator["LeafNode"]:
        """
        Polymorphic iterator to retrieve all LeafNodes contained within this element.
        Base implementation returns empty (overridden by LeafNode and Container).
        """
        return iter([])


@dataclass(frozen=True, kw_only=True, slots=True)
class LeafNode(VisualElement):
    """
    Represents an atomic code component (File/Module).
    Acts as a visual wrapper around the Shared Kernel's CodeNode.
    Composition over Mapping: Properties delegate to source_node.
    """

    source_node: CodeNode

    @property
    def layer(self) -> LayerEnum:
        if self.source_node.passport:
            return self.source_node.passport.layer
        return LayerEnum.UNDEFINED

    @property
    def raw_type(self) -> str:
        if self.source_node.passport:
            return self.source_node.passport.component_type.value
        return "UNKNOWN"

    @property
    def context(self) -> str:
        if self.source_node.passport and self.source_node.passport.context_name:
            return self.source_node.passport.context_name
        return "global"

    @property
    def outgoing_imports(self) -> Set[str]:
        return self.source_node.imports

    def walk_leaves(self) -> Iterator["LeafNode"]:
        yield self


@dataclass(frozen=True, kw_only=True, slots=True)
class VisualContainer(VisualElement):
    """
    Represents a visual grouping (Folder, Cluster, or Wrapper).
    """

    children: list[Union["VisualContainer", "LeafNode"]] = field(default_factory=list)
    is_visible: bool = True
    internal_padding: float = 0.6

    def walk_leaves(self) -> Iterator["LeafNode"]:
        for child in self.children:
            yield from child.walk_leaves()
