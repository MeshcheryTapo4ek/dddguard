from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, replace

from ...value_objects.visual_primitives import VisualElement

ASPECT_RATIO: float = 1.5


@dataclass(frozen=True, slots=True, kw_only=True)
class PackedResult:
    positioned: list[VisualElement]
    max_right: float
    max_bottom: float


@dataclass(frozen=True, slots=True, kw_only=True)
class FlowPacker:
    """
    Geometry Service: Ordered flow packing (preserves input order).
    This is critical for any "reorder to optimize metric" algorithm.
    The packer does NOT sort elements. It uses a wrap width hint to decide line breaks.
    """

    @staticmethod
    def pack(
        elements: Sequence[VisualElement],
        *,
        start_x: float,
        start_y: float,
        gap_x: float,
        gap_y: float,
        wrap_width_hint: float | None,  # Renamed from wrap_width to match caller
    ) -> PackedResult:
        if not elements:
            return PackedResult(positioned=[], max_right=start_x, max_bottom=start_y)

        max_single_width = 0.0
        total_area = 0.0

        for e in elements:
            max_single_width = max(max_single_width, e.width)
            total_area = total_area + (e.width + gap_x) * (e.height + gap_y)

        if wrap_width_hint is None:
            target_width = max(max_single_width, (total_area**0.5) * ASPECT_RATIO)
        else:
            target_width = max(max_single_width, wrap_width_hint)

        cursor_x = start_x
        cursor_y = start_y
        row_height = 0.0

        max_right = start_x
        max_bottom = start_y

        positioned: list[VisualElement] = []

        for e in elements:
            row_not_empty = cursor_x > start_x
            would_overflow = (cursor_x + e.width) > (start_x + target_width)

            if row_not_empty and would_overflow:
                cursor_y = cursor_y + row_height + gap_y
                cursor_x = start_x
                row_height = 0.0

            placed = replace(e, x=cursor_x, y=cursor_y)
            positioned.append(placed)

            row_height = max(row_height, e.height)
            cursor_x = cursor_x + e.width + gap_x

            max_right = max(max_right, placed.x + placed.width)
            max_bottom = max(max_bottom, placed.y + placed.height)

        return PackedResult(positioned=positioned, max_right=max_right, max_bottom=max_bottom)
