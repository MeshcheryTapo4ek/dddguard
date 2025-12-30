from dataclasses import dataclass
from typing import Final, Optional
import colorsys


@dataclass(frozen=True, kw_only=True, slots=True)
class EdgeColorService:
    """
    Domain Service: Generates colors for edges using the "Sharper Spectral" strategy.
    
    Logic:
    1. Simple Nodes (<= 1 outgoing edge):
       - Colored Neutral Gray (Quiet).
       
    2. Complex Nodes (> 1 outgoing edges):
       - Assigned a unique Hue using the Golden Ratio. 
       - This ensures maximal contrast between consecutive nodes (Sharp transitions).
       - Edges within the same bundle share the Hue but vary in Brightness.
    """

    # Configuration
    base_saturation: float = 0.85
    base_value: float = 0.70
    
    # Colors
    QUIET_COLOR: Final[str] = "#B0B0B0"
    
    # Magic Number for sharp color transitions (Golden Angle ~137.5 degrees)
    _golden_ratio_conjugate: Final[float] = 0.618033988749895
    
    # Bundle variation
    bundle_val_spread: float = 0.35  # Spread brightness significantly for distinction

    def get_color(
        self,
        *,
        spectral_index: Optional[int],
        total_complex_nodes: int,
        edge_index: int = 0,
        total_edges_from_node: int = 1,
    ) -> str:
        """
        Calculates the hex color.
        """
        # 1. Simple Case
        if spectral_index is None:
            return self.QUIET_COLOR

        if total_complex_nodes <= 0:
            return self.QUIET_COLOR

        # 2. Complex Case: Sharp Golden Ratio Hue
        # Instead of linear division (Rainbow), we jump by the Golden Ratio.
        # This guarantees that index N and N+1 have very different colors.
        hue = (float(spectral_index) * self._golden_ratio_conjugate) % 1.0
        
        saturation = self.base_saturation
        value = self.base_value

        # 3. Bundle Variation (Brightness spread within the bundle)
        if total_edges_from_node > 1:
            div = float(total_edges_from_node - 1)
            # Factor from -0.5 to +0.5
            factor = (float(edge_index) / div) - 0.5 if div > 0 else 0.0
            
            # Shift Value (Brightness)
            value = self.base_value + (factor * self.bundle_val_spread)
            
            # Clamp value
            value = max(0.4, min(0.95, value))

        return self._hsv_to_hex(hue, saturation, value)

    def _hsv_to_hex(self, h: float, s: float, v: float) -> str:
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))