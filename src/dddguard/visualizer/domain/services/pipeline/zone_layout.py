from ...enums import ZoneKey
from ...value_objects import (
    StyleConfig,
    VisualContainer,
    ZoneBackground,
    ZoneLayoutData,
)
from ..geometry.flow_packer import FlowPacker


class ZoneLayoutService:
    """
    Pipeline Step 4: Layout & Split Zones.
    PURE STATIC IMPLEMENTATION.
    Receives StyleConfig as an argument.
    """

    @staticmethod
    def calculate_zones(
        structure: dict[str, list[VisualContainer]], style_config: StyleConfig
    ) -> list[ZoneLayoutData]:
        architectural_zones = [
            ZoneKey.ADAPTERS_DRIVING,
            ZoneKey.PORTS_DRIVING,
            ZoneKey.APP,
            ZoneKey.DOMAIN,
            ZoneKey.COMPOSITION,
            ZoneKey.OTHER,
        ]

        zone_layouts: list[ZoneLayoutData] = []
        current_y = style_config.HEADER_HEIGHT
        processed_layers = set()

        for z_key in architectural_zones:
            layer_group = ZoneLayoutService._get_layer_group(z_key)

            if layer_group in processed_layers:
                continue
            processed_layers.add(layer_group)

            is_split_zone = layer_group in ("ADAPTERS", "PORTS")

            # Gather content
            if is_split_zone:
                driving = structure.get(f"{layer_group}_DRIVING", [])
                driven = structure.get(f"{layer_group}_DRIVEN", [])
                other = structure.get(f"{layer_group}_OTHER", [])
                has_content = bool(driving or driven or other)
            else:
                items = structure.get(z_key.value, [])
                has_content = bool(items)

            if not has_content:
                continue

            zone_bg_y = current_y

            if is_split_zone:
                layout_res = ZoneLayoutService._layout_split_zone(
                    base_name=layer_group,
                    driving=driving,
                    driven=driven,
                    other=other,
                    start_y=current_y,
                    style_config=style_config,
                )
            else:
                layout_res = ZoneLayoutService._layout_single_zone(
                    z_name=z_key.value,
                    items=items,
                    start_y=current_y,
                    style_config=style_config,
                )

            current_y = zone_bg_y + layout_res.height + style_config.ZONE_GAP_Y
            zone_layouts.append(layout_res)

        return zone_layouts

    @staticmethod
    def _get_layer_group(key: ZoneKey) -> str:
        if "ADAPTERS" in key.value:
            return "ADAPTERS"
        if "PORTS" in key.value:
            return "PORTS"
        return key.value

    @staticmethod
    def _layout_single_zone(
        z_name: str,
        items: list[VisualContainer],
        start_y: float,
        style_config: StyleConfig,
    ) -> ZoneLayoutData:
        start_x = style_config.ZONE_HEADER_WIDTH

        packed = FlowPacker.pack(
            elements=items,
            start_x=start_x,
            start_y=start_y,
            gap_x=style_config.CONTAINER_GAP_X,
            gap_y=style_config.CONTAINER_GAP_Y,
            wrap_width_hint=None,  # Updated arg name
        )

        w = packed.max_right
        h = packed.max_bottom - start_y

        bg_color = style_config.ZONE_BG_COLORS.get(ZoneKey(z_name), "#f0f0f0")

        bg = ZoneBackground(
            x_rel=style_config.ZONE_HEADER_WIDTH,
            y_rel=start_y,
            width=max(0.0, w - style_config.ZONE_HEADER_WIDTH),
            height=h,
            color=bg_color,
            side="center",
        )

        return ZoneLayoutData(
            name=z_name,
            y_start=start_y,
            height=h,
            width=w,
            items=packed.positioned,
            backgrounds=[bg],
        )

    @staticmethod
    def _layout_split_zone(
        base_name: str,
        driving: list,
        driven: list,
        other: list,
        start_y: float,
        style_config: StyleConfig,
    ) -> ZoneLayoutData:
        current_y = start_y
        all_items = []
        backgrounds = []
        max_w = style_config.ZONE_HEADER_WIDTH

        # 1. Other (Center/Full)
        if other:
            packed_other = FlowPacker.pack(
                elements=other,
                start_x=style_config.ZONE_HEADER_WIDTH,
                start_y=current_y,
                gap_x=style_config.CONTAINER_GAP_X,
                gap_y=style_config.CONTAINER_GAP_Y,
                wrap_width_hint=None,  # Updated arg name
            )
            all_items.extend(packed_other.positioned)
            h_other = packed_other.max_bottom - current_y
            w_other = packed_other.max_right

            try:
                bg_key = ZoneKey(f"{base_name}_OTHER")
                bg_color = style_config.ZONE_BG_COLORS.get(bg_key, "#f0f0f0")
            except ValueError:
                bg_color = "#f0f0f0"

            backgrounds.append(
                ZoneBackground(
                    x_rel=style_config.ZONE_HEADER_WIDTH,
                    y_rel=current_y,
                    width=max(0.0, w_other - style_config.ZONE_HEADER_WIDTH),
                    height=h_other,
                    color=bg_color,
                    side="center",
                )
            )
            current_y = packed_other.max_bottom + style_config.ROW_GAP_Y
            max_w = max(max_w, w_other)

        # 2. Split Columns (Driving Left, Driven Right)
        start_x_driving = style_config.ZONE_HEADER_WIDTH
        split_start_y = current_y + style_config.SPLIT_LABEL_HEIGHT

        # Pack Left
        packed_driving = FlowPacker.pack(
            elements=driving,
            start_x=start_x_driving,
            start_y=split_start_y,
            gap_x=style_config.CONTAINER_GAP_X,
            gap_y=style_config.CONTAINER_GAP_Y,
            wrap_width_hint=None,  # Updated arg name
        )

        w_driving = max(style_config.MIN_BLOCK_WIDTH, packed_driving.max_right - start_x_driving)
        col_gap = style_config.MIN_BLOCK_WIDTH * 0.5
        start_x_driven = packed_driving.max_right + col_gap

        # Pack Right
        packed_driven = FlowPacker.pack(
            elements=driven,
            start_x=start_x_driven,
            start_y=split_start_y,
            gap_x=style_config.CONTAINER_GAP_X,
            gap_y=style_config.CONTAINER_GAP_Y,
            wrap_width_hint=None,  # Updated arg name
        )

        w_driven = packed_driven.max_right - start_x_driven

        all_items.extend(packed_driving.positioned)
        all_items.extend(packed_driven.positioned)

        split_bottom = max(packed_driving.max_bottom, packed_driven.max_bottom, split_start_y + 1.0)
        split_height = split_bottom - current_y

        # Colors
        try:
            c_driving = style_config.ZONE_BG_COLORS.get(ZoneKey(f"{base_name}_DRIVING"), "#e8f5e9")
            c_driven = style_config.ZONE_BG_COLORS.get(ZoneKey(f"{base_name}_DRIVEN"), "#fffde7")
        except ValueError:
            c_driving, c_driven = "#fff", "#fff"

        backgrounds.append(
            ZoneBackground(
                x_rel=start_x_driving,
                y_rel=current_y,
                width=w_driving,
                height=split_height,
                color=c_driving,
                side="left",
                label="DRIVING",
            )
        )
        backgrounds.append(
            ZoneBackground(
                x_rel=start_x_driven,
                y_rel=current_y,
                width=w_driven,
                height=split_height,
                color=c_driven,
                side="right",
                label="DRIVEN",
            )
        )

        max_w = max(max_w, packed_driven.max_right)
        total_height = split_bottom - start_y

        return ZoneLayoutData(
            name=base_name,
            y_start=start_y,
            height=total_height,
            width=max_w,
            items=all_items,
            backgrounds=backgrounds,
        )
