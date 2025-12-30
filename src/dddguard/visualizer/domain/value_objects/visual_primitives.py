from dataclasses import dataclass, field
from typing import List, Dict, Union, Optional

from dddguard.shared import LayerEnum


@dataclass(frozen=True, kw_only=True, slots=True)
class VisualElement:
    """
    Base value object for any element in the diagram (Node or Container).
    Position (x, y) is relative to its parent container.
    """
    x: float
    y: float
    width: float
    height: float
    label: str
    id: str  # Unique identifier for edge linking
    color: str = "none"


@dataclass(frozen=True, kw_only=True, slots=True)
class LeafNode(VisualElement):
    """
    Represents an atomic code component (File/Module).
    """
    layer: Union[LayerEnum, str]
    raw_type: str
    context: str
    outgoing_imports: List[Dict[str, str]] = field(default_factory=list)


@dataclass(frozen=True, kw_only=True, slots=True)
class VisualContainer(VisualElement):
    """
    Represents a visual grouping (Folder, Cluster, or Wrapper).
    """
    children: List[Union['VisualContainer', 'LeafNode']] = field(default_factory=list)
    is_visible: bool = True
    internal_padding: float = 0.6