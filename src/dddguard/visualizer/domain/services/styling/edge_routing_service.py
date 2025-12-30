from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True, kw_only=True, slots=True)
class EdgeRoutingService:
    """
    Domain Service: computes anchor style for edges (exit/entry points).
    Enforces "Waterfall" routing for layered architecture:
    - Downward dependencies always Exit Bottom -> Enter Top.
    - Side-by-side dependencies use Left/Right.
    """

    # How much vertical overlap is allowed before we consider them "side-by-side"
    # 0.5 means if they overlap by 50% height, treat as horizontal row.
    overlap_threshold: float = 0.5

    def anchor_style(
        self,
        src: Tuple[float, float, float, float],
        tgt: Tuple[float, float, float, float],
        out_idx: int,
        out_total: int,
        in_idx: int,
        in_total: int,
    ) -> str:
        """
        Returns a style string with exitX/exitY/entryX/entryY for mxGraph edges.
        """
        # Unpack geometries: x, y, width, height
        sx, sy, sw, sh = src
        tx, ty, tw, th = tgt

        # Calculate boundaries
        src_top = sy
        src_bottom = sy + sh
        tgt_top = ty
        tgt_bottom = ty + th

        # --- Determine Relative Position ---

        # 1. Check for Downward Flow (Standard Layer Dependency)
        # If the Target's top is clearly below the Source's "center-ish"
        # We use a slight buffer so slight misalignments don't break logic
        if tgt_top >= (src_bottom - (sh * (1 - self.overlap_threshold))):
            direction = "DOWN"

        # 2. Check for Upward Flow (Callbacks, or Mistakes)
        elif tgt_bottom <= (src_top + (sh * (1 - self.overlap_threshold))):
            direction = "UP"

        # 3. Otherwise, they are effectively on the same horizontal row (Side-by-Side)
        else:
            direction = "SIDE"

        # --- Helper for distribution ---
        def rel_pos_zero_based(index_zero: int, total: int) -> float:
            if total <= 1:
                return 0.5
            # Distribute evenly between 0 and 1
            return float(index_zero + 1) / float(total + 1)

        out_pos = rel_pos_zero_based(out_idx, out_total)
        # For incoming, handle 1-based index if passed that way, or clamp
        in_zero_based = max(in_idx - 1, 0)
        in_pos = rel_pos_zero_based(in_zero_based, in_total)

        parts = []

        if direction == "DOWN":
            # Waterfall: Exit Bottom, Enter Top
            parts.append(f"exitX={out_pos:.2f};exitY=1;exitDx=0;exitDy=0;")
            parts.append(f"entryX={in_pos:.2f};entryY=0;entryDx=0;entryDy=0;")

        elif direction == "UP":
            # Reverse Waterfall: Exit Top, Enter Bottom
            parts.append(f"exitX={out_pos:.2f};exitY=0;exitDx=0;exitDy=0;")
            parts.append(f"entryX={in_pos:.2f};entryY=1;entryDx=0;entryDy=0;")

        else:  # SIDE
            # Determine Left or Right based on center X
            sc_x = sx + sw / 2.0
            tc_x = tx + tw / 2.0

            if tc_x > sc_x:
                # Target is to the Right -> Exit Right, Enter Left
                parts.append(f"exitX=1;exitY={out_pos:.2f};exitDx=0;exitDy=0;")
                parts.append(f"entryX=0;entryY={in_pos:.2f};entryDx=0;entryDy=0;")
            else:
                # Target is to the Left -> Exit Left, Enter Right
                parts.append(f"exitX=0;exitY={out_pos:.2f};exitDx=0;exitDy=0;")
                parts.append(f"entryX=1;entryY={in_pos:.2f};entryDx=0;entryDy=0;")

        return "".join(parts)