from dataclasses import dataclass, field
from typing import List

from ..value_objects.visual_primitives import Box, ZoneBackground


@dataclass(frozen=True, kw_only=True, slots=True)
class TowerZone:
    """
    Entity: A horizontal slice of a tower (e.g. 'Domain Layer' or 'App Layer').
    Part of the ContextTower Aggregate.
    """
    name: str
    y_bottom: float
    height: float
    backgrounds: List[ZoneBackground] = field(default_factory=list)
    nodes: List[Box] = field(default_factory=list)


@dataclass(frozen=True, kw_only=True, slots=True)
class ContextTower:
    """
    Aggregate Root: Visual representation of a single Bounded Context.
    Ensures the vertical stack of zones remains consistent.
    """
    name: str
    x: float
    width: float
    zones: List[TowerZone]
    forced_height: float = 0.0