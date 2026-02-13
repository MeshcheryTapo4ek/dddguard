import colorsys
from dataclasses import dataclass
from typing import Final

BASE_SATURATION: Final[float] = 0.85
BASE_VALUE: Final[float] = 0.70

QUIET_COLOR: Final[str] = "#FFFFFF"

GOLDEN_RATIO_CONJUGATE: Final[float] = 0.618033988749895

BUNDLE_VALUE_SPREAD: Final[float] = 0.35


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

    @staticmethod
    def get_color(
        *,
        spectral_index: int | None,
        total_complex_nodes: int,
        edge_index: int = 0,
        total_edges_from_node: int = 1,
    ) -> str:
        """
        Calculates the hex color.
        """
        # 1. Simple Case
        if spectral_index is None:
            return QUIET_COLOR

        if total_complex_nodes <= 0:
            return QUIET_COLOR

        # 2. Complex Case: Sharp Golden Ratio Hue
        # Instead of linear division (Rainbow), we jump by the Golden Ratio.
        # This guarantees that index N and N+1 have very different colors.
        hue = (float(spectral_index) * GOLDEN_RATIO_CONJUGATE) % 1.0
        value = BASE_VALUE
        # 3. Bundle Variation (Brightness spread within the bundle)
        if total_edges_from_node >= 1:
            div = float(total_edges_from_node - 1)
            # Factor from -0.5 to +0.5
            factor = (float(edge_index) / div) - 0.5 if div > 0 else 0.0

            # Shift Value (Brightness)
            value = BASE_VALUE + (factor * BUNDLE_VALUE_SPREAD)

            # Clamp value
            value = max(0.4, min(0.95, value))

        r, g, b = colorsys.hsv_to_rgb(hue, BASE_SATURATION, value)

        return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"
