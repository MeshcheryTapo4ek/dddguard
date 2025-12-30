from dataclasses import dataclass, field
from typing import List

from ..value_objects.visual_primitives import VisualContainer, VisualElement


@dataclass(frozen=True, kw_only=True, slots=True)
class ZoneBackground:
    """
    Value Object: Colored background rect for a Zone.
    """
    x_rel: float
    y_rel: float
    width: float
    height: float
    color: str
    side: str  # 'left', 'right', 'center'
    label: str | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class TowerZone:
    """
    Entity: A horizontal fixed section of a tower (e.g. 'Domain Layer').
    Part of the ContextTower Aggregate.
    """
    name: str
    y_bottom: float
    height: float
    backgrounds: List[ZoneBackground] = field(default_factory=list)
    
    # Updated: Holds top-level containers (Left/Center/Right groups)
    containers: List[VisualContainer] = field(default_factory=list)


@dataclass(frozen=True, kw_only=True, slots=True)
class ContextTower:
    """
    Aggregate Root: Visual representation of a single Bounded Context.
    """
    name: str
    x: float
    width: float
    zones: List[TowerZone]
    forced_height: float = 0.0