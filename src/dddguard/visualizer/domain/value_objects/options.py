from dataclasses import dataclass, field

from dddguard.shared.domain import DirectionEnum, LayerEnum

from ..enums import ZoneKey


@dataclass(frozen=True, slots=True, kw_only=True)
class OptimizationConfig:
    """
    Configuration for container layout optimization.
    """

    max_children_guard: int = 28
    iterations: int = 1000
    restarts: int = 100

    lambda_y: float = 1.0
    shape_penalty: float = 0.02

    upward_penalty: float = 2.0  # Cost multiplier for upward arrows
    external_attraction: float = 1.5  # Weight for external anchors

    # Accept only improvements (deterministic hill-climb).
    allow_worse_moves: bool = False


@dataclass(frozen=True, slots=True, kw_only=True)
class VisualizationConfig:
    """
    Configuration flags for the rendering engine.
    """

    # Visibility
    show_errors: bool = False

    # Graph Filtering (Split Logic)
    hide_root_arrows: bool = True
    hide_shared_arrows: bool = True

    # Output
    output_file: str = "architecture.drawio"


@dataclass(frozen=True, slots=True)
class StyleConfig:
    """
    Visual constants and color mappings.
    Passed as a context object to layout algorithms.
    """

    # Dimensions
    NODE_HEIGHT: float = 1.6
    MIN_NODE_WIDTH: float = 3.0
    MIN_BLOCK_WIDTH: float = 4.0
    CHAR_WIDTH_FACTOR: float = 0.15
    NODE_PAD_X_INNER: float = 0.4

    CONTAINER_PAD_X: float = 0.6
    CONTAINER_PAD_Y: float = 0.6
    CONTAINER_GAP_X: float = 0.0
    CONTAINER_GAP_Y: float = 0.0
    LEAF_GAP_X: float = 0.5
    LEAF_GAP_Y: float = 0.5

    ZONE_GAP_Y: float = 0.5
    ROW_GAP_Y: float = 0.5
    TOWER_PAD_X: float = 2.0

    HEADER_HEIGHT: float = 1.2
    ZONE_HEADER_WIDTH: float = 1.5
    SPLIT_LABEL_HEIGHT: float = 0.8

    # Colors
    DEFAULT_COLOR: str = "#ffffff"

    NODE_COLORS: dict[str, str] = field(
        default_factory=lambda: {
            "DOMAIN": "#80d8ff",
            "APP": "#ea80fc",
            "ADAPTERS_DRIVING": "#b9f6ca",
            "ADAPTERS_DRIVEN": "#ffe57f",
            "PORTS_DRIVING": "#b3e5fc",
            "PORTS_DRIVEN": "#cfd8dc",
            "COMPOSITION": "#ff8a80",
            "GLOBAL": "#e0e0e0",
        }
    )

    ZONE_BG_COLORS: dict[ZoneKey, str] = field(
        default_factory=lambda: {
            ZoneKey.DOMAIN: "#e1f5fe",
            ZoneKey.APP: "#f3e5f5",
            ZoneKey.COMPOSITION: "#ffebee",
            ZoneKey.OTHER: "#fafafa",
            # Split Zones
            ZoneKey.ADAPTERS_DRIVING: "#e8f5e9",
            ZoneKey.ADAPTERS_DRIVEN: "#fffde7",
            ZoneKey.PORTS_DRIVING: "#e1f5fe",
            ZoneKey.PORTS_DRIVEN: "#eceff1",
        }
    )

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

    def get_zone_bg(self, zone_key: ZoneKey) -> str:
        return self.ZONE_BG_COLORS.get(zone_key, self.ZONE_BG_COLORS[ZoneKey.OTHER])

    def format_label(self, module_path: str) -> str:
        simple_name = module_path.split(".")[-1]
        if simple_name.lower().endswith(".py"):
            simple_name = simple_name[:-3]
        return f"{simple_name}"

    def calculate_node_width(self, label: str) -> float:
        calc_width = (len(label) * self.CHAR_WIDTH_FACTOR) + (self.NODE_PAD_X_INNER * 2)
        return max(calc_width, self.MIN_NODE_WIDTH)


style = StyleConfig()
