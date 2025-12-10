from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional

from dddguard.shared import ContextLayerEnum


@dataclass(frozen=True, kw_only=True, slots=True)
class Box:
    """
    Value Object: Represents a rectangular node on the canvas.
    Contains geometric data and minimal metadata for linking.
    """
    x: float
    y: float
    width: float
    height: float
    label: str
    color: str = "#ffffff"
    
    # Metadata for linking (Reference to the source module)
    id: str = ""
    layer: ContextLayerEnum | str = ""
    raw_type: str = ""
    context: str = "" 
    
    # Minimal import info for rendering arrows
    # format: [{"module": "target.path"}, ...]
    outgoing_imports: List[Dict[str, str]] = field(default_factory=list)

    @property
    def center(self) -> Tuple[float, float]:
        return (self.x + self.width / 2, self.y + self.height / 2)


@dataclass(frozen=True, kw_only=True, slots=True)
class ZoneBackground:
    """
    Value Object: A colored background rectangle for a specific zone.
    Used to visually group related layers (e.g., "Driving Adapters").
    """
    x_rel: float
    y_rel: float
    width: float
    height: float
    color: str
    label: Optional[str] = None
    label_align: str = "left"
    side: str = "center"