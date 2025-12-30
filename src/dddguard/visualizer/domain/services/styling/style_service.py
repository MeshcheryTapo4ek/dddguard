from dataclasses import dataclass
from typing import Dict, ClassVar

from dddguard.shared import LayerEnum, DirectionEnum


@dataclass(frozen=True, kw_only=True, slots=True)
class StyleService:
    """
    Domain Service: Configuration provider for visual styles.
    """

    NODE_HEIGHT: ClassVar[float] = 1.6
    MIN_NODE_WIDTH: ClassVar[float] = 3.0
    MIN_BLOCK_WIDTH: ClassVar[float] = 4.0

    # Containers: keep padding for node spacing, but no gaps between nested containers
    CONTAINER_PAD_X: ClassVar[float] = 0.6
    CONTAINER_PAD_Y: ClassVar[float] = 0.6

    CONTAINER_GAP_X: ClassVar[float] = 0.0
    CONTAINER_GAP_Y: ClassVar[float] = 0.0

    # Leaves: keep gaps for readability/arrows
    LEAF_GAP_X: ClassVar[float] = 0.5
    LEAF_GAP_Y: ClassVar[float] = 0.5

    ZONE_GAP_Y: ClassVar[float] = 0.5
    ROW_GAP_Y: ClassVar[float] = 0.5
    TOWER_PAD_X: ClassVar[float] = 2.0
    

    CHAR_WIDTH_FACTOR: ClassVar[float] = 0.15
    NODE_PAD_X_INNER: ClassVar[float] = 0.4

    HEADER_HEIGHT: ClassVar[float] = 1.2
    ZONE_HEADER_WIDTH: ClassVar[float] = 1.5

    # Reserved top area inside split backgrounds for DRIVING/DRIVEN labels
    SPLIT_LABEL_HEIGHT: ClassVar[float] = 0.8

    DEFAULT_COLOR: ClassVar[str] = "#ffffff"

    NODE_COLORS: ClassVar[Dict[str, str]] = {
        "DOMAIN": "#80d8ff",
        "APP": "#ea80fc",

        "ADAPTERS_DRIVING": "#b9f6ca",
        "ADAPTERS_DRIVEN": "#ffe57f",
        "ADAPTERS_ANY": "#fff9c4",

        "PORTS_DRIVING": "#b3e5fc",
        "PORTS_DRIVEN": "#cfd8dc",
        "PORTS_ANY": "#eceff1",

        "COMPOSITION": "#ff8a80",
        "GLOBAL": "#e0e0e0",
    }

    ZONE_BG_COLORS: ClassVar[Dict[str, str]] = {
        "ADAPTERS_BG": "#fff8e1",
        "PORTS_BG": "#eceff1",
        "APP_BG": "#f3e5f5",
        "DOMAIN_BG": "#e1f5fe",
        "COMPOSITION_BG": "#ffebee",
        "OTHER": "#fafafa",

        "ADAPTERS_DRIVING_BG": "#e8f5e9",
        "ADAPTERS_DRIVEN_BG": "#fffde7",

        "PORTS_DRIVING_BG": "#e1f5fe",
        "PORTS_DRIVEN_BG": "#eceff1",
    }

    def get_node_color(self, layer: LayerEnum, direction: DirectionEnum) -> str:
        if layer == LayerEnum.ADAPTERS:
            if direction == DirectionEnum.DRIVING:
                return self.NODE_COLORS["ADAPTERS_DRIVING"]
            if direction == DirectionEnum.DRIVEN:
                return self.NODE_COLORS["ADAPTERS_DRIVEN"]
            return self.NODE_COLORS["ADAPTERS_ANY"]

        if layer == LayerEnum.PORTS:
            if direction == DirectionEnum.DRIVING:
                return self.NODE_COLORS["PORTS_DRIVING"]
            if direction == DirectionEnum.DRIVEN:
                return self.NODE_COLORS["PORTS_DRIVEN"]
            return self.NODE_COLORS["PORTS_ANY"]

        return self.NODE_COLORS.get(layer.value, self.DEFAULT_COLOR)

    def format_label(self, module_path: str, type_name: str) -> str:
        simple_name = module_path.split(".")[-1]
        if simple_name.lower().endswith(".py"):
            simple_name = simple_name[:-3]
        return f"{simple_name}"

    def calculate_node_width(self, label: str) -> float:
        calc_width = (len(label) * self.CHAR_WIDTH_FACTOR) + (self.NODE_PAD_X_INNER * 2)
        return max(calc_width, self.MIN_NODE_WIDTH)
