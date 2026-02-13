from dataclasses import dataclass, field

from .visual_primitives import VisualContainer
from .zone_background import ZoneBackground


@dataclass(frozen=True, kw_only=True, slots=True)
class ZoneLayoutData:
    """
    Value Object: Intermediate calculation result for a single zone layout.
    """

    name: str
    y_start: float
    height: float
    width: float
    items: list[VisualContainer] = field(default_factory=list)
    backgrounds: list[ZoneBackground] = field(default_factory=list)
