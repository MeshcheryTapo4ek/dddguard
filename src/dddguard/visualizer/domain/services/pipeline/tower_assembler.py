from dataclasses import replace

# Aggregate from context_tower
from ...context_tower_aggregate import ContextTower, TowerZone

# VOs from value_objects
from ...value_objects import StyleConfig, ZoneBackground, ZoneLayoutData


class TowerAssemblerService:
    """
    Pipeline Step 5: Assembly.
    PURE STATIC IMPLEMENTATION.
    """

    @staticmethod
    def assemble(
        context_name: str, layouts: list[ZoneLayoutData], style_config: StyleConfig
    ) -> ContextTower:
        max_tower_width = style_config.MIN_BLOCK_WIDTH
        for z in layouts:
            max_tower_width = max(max_tower_width, z.width)

        final_zones = TowerAssemblerService._stretch_backgrounds(
            layouts, max_tower_width, style_config
        )

        # Calculate total height based on the last zone
        forced_height = 0.0
        if final_zones:
            forced_height = final_zones[-1].y_bottom

        return ContextTower(
            name=context_name,
            x=0.0,  # Global X is set by the Use Case or Workflow later
            width=max_tower_width,
            zones=final_zones,
            forced_height=forced_height,
        )

    @staticmethod
    def _stretch_backgrounds(
        layouts: list[ZoneLayoutData], max_width: float, style_config: StyleConfig
    ) -> list[TowerZone]:
        final_zones: list[TowerZone] = []

        for z in layouts:
            final_backgrounds: list[ZoneBackground] = []

            for bg in z.backgrounds:
                if bg.side == "left":
                    final_backgrounds.append(bg)
                elif bg.side == "right":
                    # Anchor right column to the right edge
                    new_x = max_width - bg.width
                    final_backgrounds.append(replace(bg, x_rel=new_x))
                else:  # Center
                    # Stretch to full width
                    full_w = max_width - style_config.ZONE_HEADER_WIDTH
                    final_backgrounds.append(replace(bg, width=full_w))

            # Gap filling for split zones
            has_left = any(b.side == "left" for b in final_backgrounds)
            has_right = any(b.side == "right" for b in final_backgrounds)

            if has_left and has_right:
                rbg = next(b for b in final_backgrounds if b.side == "right")
                lbg = next(b for b in final_backgrounds if b.side == "left")
                lbg_idx = final_backgrounds.index(lbg)

                # Fill the void
                gap = rbg.x_rel - (lbg.x_rel + lbg.width)
                if gap > 0:
                    final_backgrounds[lbg_idx] = replace(lbg, width=lbg.width + gap)

            final_zones.append(
                TowerZone(
                    name=z.name,
                    y_bottom=z.y_start + z.height,
                    height=z.height,
                    backgrounds=final_backgrounds,
                    containers=z.items,
                )
            )
        return final_zones
