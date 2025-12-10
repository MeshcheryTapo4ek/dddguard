from dataclasses import dataclass
from typing import Final
import colorsys


@dataclass(frozen=True, kw_only=True, slots=True)
class EdgeColorService:
    """
    Domain Service: Generates deterministic colors for edges.
    Uses Golden Ratio for distinct nodes, and Analogous Spread for bundled edges.
    """
    base_saturation: float = 0.85
    
    _fallback_color: Final[str] = "#444444"
    _golden_ratio_conjugate: Final[float] = 0.618033988749895

    # Configuration for bundles (multiple arrows from same node)
    bundle_hue_spread: float = 0.08   # Spread hue by +/- 4% (creates analogous colors)
    bundle_val_spread: float = 0.4    # Spread brightness significantly (Dark <-> Light)

    def get_color_for_source(
        self,
        node_index: int,
        total_nodes: int,
        edge_index: int = 0,
        total_edges_from_node: int = 1,
    ) -> str:
        """
        Returns a hex color string.
        Logic:
        1. Node Identity: Golden Ratio Hue (High contrast between neighbors).
        2. Bundle Identity: Analogous Hue Shift + Brightness Spread (High contrast within bundle).
        """
        if total_nodes <= 0:
            return self._fallback_color

        # 1. Base Hue (Golden Angle)
        base_hue = (float(node_index) * self._golden_ratio_conjugate) % 1.0

        hue = base_hue
        saturation = self.base_saturation
        value = 0.75 # Default brightness base

        # 2. Bundle Variation (if multiple edges)
        if total_edges_from_node > 1:
            # Normalized factor from -0.5 (first edge) to +0.5 (last edge)
            div = float(total_edges_from_node - 1)
            if div == 0: div = 1.0
            
            factor = (float(edge_index) / div) - 0.5

            # A. Shift Hue slightly (e.g. Blue -> Teal ... Blue -> Purple)
            # This makes individual lines easy to trace
            hue = (base_hue + (factor * self.bundle_hue_spread)) % 1.0

            # B. Shift Value (Brightness) aggressively
            # Range: roughly 0.55 (Dark) to 0.95 (Bright)
            value = 0.75 + (factor * self.bundle_val_spread)
            
            # Clamp value to stay visible on white background
            value = max(0.4, min(0.95, value))

        return self._hsv_to_hex(hue, saturation, value)

    def _hsv_to_hex(self, h: float, s: float, v: float) -> str:
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))