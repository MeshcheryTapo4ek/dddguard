from dataclasses import dataclass, field

from .value_objects import VisualContainer, ZoneBackground


@dataclass(frozen=True, kw_only=True, slots=True)
class TowerZone:
    """
    Entity: A horizontal fixed section of a tower (e.g. 'Domain Layer').
    Part of the ContextTower Aggregate.
    """

    name: str
    y_bottom: float
    height: float
    backgrounds: list[ZoneBackground] = field(default_factory=list)

    # Updated: Holds top-level containers (Left/Center/Right groups)
    containers: list[VisualContainer] = field(default_factory=list)


@dataclass(frozen=True, kw_only=True, slots=True)
class ContextTower:
    """
    Aggregate Root: Visual representation of a single Bounded Context.
    """

    name: str
    x: float
    width: float
    zones: list[TowerZone]
    forced_height: float = 0.0
