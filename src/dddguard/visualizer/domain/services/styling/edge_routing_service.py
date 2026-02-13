from dataclasses import dataclass

OVERLAP_THRESHOLD = 0.5


@dataclass(frozen=True, kw_only=True, slots=True)
class EdgeRoutingService:
    """
    Domain Service: computes anchor style for edges.
    Refactored to support grouped routing (Distribution).
    """

    @staticmethod
    def resolve_direction(
        src: tuple[float, float, float, float],
        tgt: tuple[float, float, float, float],
    ) -> str:
        """
        Pure geometry check: Where is Target relative to Source?
        Returns: 'DOWN', 'UP', 'SIDE_LEFT', 'SIDE_RIGHT'
        """
        sx, sy, sw, sh = src
        tx, ty, tw, th = tgt

        src_bottom = sy + sh
        src_top = sy
        tgt_top = ty
        tgt_bottom = ty + th

        # 1. Downward (Waterfall)
        if tgt_top >= (src_bottom - (sh * (1 - OVERLAP_THRESHOLD))):
            return "DOWN"

        # 2. Upward (Reverse Waterfall)
        if tgt_bottom <= (src_top + (sh * (1 - OVERLAP_THRESHOLD))):
            return "UP"

        # 3. Side-by-Side
        sc_x = sx + sw / 2.0
        tc_x = tx + tw / 2.0

        return "SIDE_RIGHT" if tc_x > sc_x else "SIDE_LEFT"

    @staticmethod
    def calculate_anchor(
        direction: str,
        out_idx: int,
        out_total: int,
        in_idx: int,
        in_total: int,
    ) -> str:
        """
        Generates the Draw.io connection points string based on pre-calculated groups.
        """

        def rel_pos(index_zero: int, total: int) -> float:
            # Distribute evenly: 1 item -> 0.5; 2 items -> 0.33, 0.66
            if total <= 0:
                return 0.5
            return float(index_zero + 1) / float(total + 1)

        out_pos = rel_pos(out_idx, out_total)
        in_pos = rel_pos(in_idx, in_total)

        if direction == "DOWN":
            # Exit Bottom -> Enter Top
            return (
                f"exitX={out_pos:.2f};exitY=1;exitDx=0;exitDy=0;"
                f"entryX={in_pos:.2f};entryY=0;entryDx=0;entryDy=0;"
            )

        if direction == "UP":
            # Exit Top -> Enter Bottom
            return (
                f"exitX={out_pos:.2f};exitY=0;exitDx=0;exitDy=0;"
                f"entryX={in_pos:.2f};entryY=1;entryDx=0;entryDy=0;"
            )

        if direction == "SIDE_RIGHT":
            # Exit Right -> Enter Left
            return (
                f"exitX=1;exitY={out_pos:.2f};exitDx=0;exitDy=0;"
                f"entryX=0;entryY={in_pos:.2f};entryDx=0;entryDy=0;"
            )

        # SIDE_LEFT
        # Exit Left -> Enter Right
        return (
            f"exitX=0;exitY={out_pos:.2f};exitDx=0;exitDy=0;"
            f"entryX=1;entryY={in_pos:.2f};entryDx=0;entryDy=0;"
        )
