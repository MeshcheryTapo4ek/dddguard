from dataclasses import dataclass
from typing import Dict, ClassVar
from dddguard.shared import ContextLayerEnum


@dataclass(frozen=True, kw_only=True, slots=True)
class StyleService:
    """
    Domain Service: Configuration provider for visual styles.
    Updated for larger nodes and better spacing.
    """
    # --- Dimensions  ---
    NODE_HEIGHT: ClassVar[float] = 1.6 
    
    # Base node width
    MIN_NODE_WIDTH: ClassVar[float] = 3.5
    
    # Minimum width for the Driving/Driven background blocks
    MIN_BLOCK_WIDTH: ClassVar[float] = 5.5 
    
    # --- Spacing (Increased indents) ---
    NODE_GAP_X: ClassVar[float] = 0.8         
    NODE_GAP_Y: ClassVar[float] = 0.8         
    ROW_PAD_Y: ClassVar[float] = 1.0          # Indent inside the row
    ZONE_GAP_Y: ClassVar[float] = 0.6         # Indent between zones
    
    HEADER_HEIGHT: ClassVar[float] = 1.8
    TOWER_PAD_X: ClassVar[float] = 2.5
    ZONE_HEADER_WIDTH: ClassVar[float] = 2.8
    
    CHAR_WIDTH_FACTOR: ClassVar[float] = 0.17
    NODE_PAD_X_INNER: ClassVar[float] = 0.6
    
    # Gap between Driving and Driven blocks
    SPLIT_GAP_X: ClassVar[float] = 0.6 
    
    # Padding inside the colored block (around the nodes)
    BLOCK_PAD_X: ClassVar[float] = 0.8

    # --- Colors (Vivid Palette) ---
    NODE_COLORS: ClassVar[Dict[ContextLayerEnum, str]] = {
        ContextLayerEnum.DOMAIN: "#80d8ff",            # Bright Light Blue
        ContextLayerEnum.APP: "#ea80fc",               # Bright Purple
        ContextLayerEnum.DRIVING_ADAPTERS: "#b9f6ca",  # Bright Mint Green
        ContextLayerEnum.DRIVEN_ADAPTERS: "#ffe57f",   # Bright Amber
        ContextLayerEnum.DRIVING_PORTS: "#cfd8dc",     # Blue Grey
        ContextLayerEnum.DRIVEN_PORTS: "#cfd8dc",
        ContextLayerEnum.COMPOSITION: "#ff8a80",       # Red Accent
        ContextLayerEnum.OTHER: "#ffffff"
    }

    ZONE_BG_COLORS: ClassVar[Dict[str, str]] = {
        "DRIVING_BG": "#ccfccb",    # Vivid Pale Green
        "DRIVEN_BG": "#ffecb3",     # Vivid Pale Orange
        "APP_BG": "#f3e5f5",        
        "DOMAIN_BG": "#e1f5fe",        
        "COMPOSITION_BG": "#ffebee", 
        "OTHER": "#fafafa"
    }

    def get_node_color(self, layer: ContextLayerEnum | str) -> str:
        if isinstance(layer, str):
            try:
                layer = ContextLayerEnum(layer)
            except ValueError:
                return "#ffffff"
        return self.NODE_COLORS.get(layer, "#ffffff")

    def format_label(self, module_path: str, type_name: str) -> str:
        simple_name = module_path.split(".")[-1]
        if simple_name.lower().endswith(".py"):
            simple_name = simple_name[:-3]
        return f"{simple_name}"

    def calculate_node_width(self, label: str) -> float:
        calc_width = (len(label) * self.CHAR_WIDTH_FACTOR) + (self.NODE_PAD_X_INNER * 2)
        return max(calc_width, self.MIN_NODE_WIDTH)