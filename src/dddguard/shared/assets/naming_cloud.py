from dddguard.shared.domain import DDD_NAMING_REGISTRY, DirectionEnum


def get_naming_cloud_html() -> str:
    """
    Generates dynamic HTML representing the project's architectural naming protocols.
    Traverses the SRM v2.0 registry to build a categorized 'Tag Cloud'.
    """
    # --- UI Styles ---
    H3_STYLE = (
        "margin-top: 0; margin-bottom: 5px; color: #34495E; font-size: 14px; font-weight: bold;"
    )
    TXT_STYLE = "font-family: Helvetica; color: #333; font-size: 11px; line-height: 1.4;"
    TAG_STYLE = (
        "display: inline-block; background-color: #EBF5FB; color: #2E86C1; "
        "padding: 1px 4px; margin: 1px; border-radius: 3px; font-size: 10px; border: 1px solid #D6EAF8;"
    )
    TYPE_HEADER_STYLE = "font-weight: bold; color: #555; margin-top: 4px; font-size: 11px;"

    # 1. Process nested registry into a flat display structure
    # Structure: group_name -> List[(type_name, tokens)]
    grouped_display: dict[str, list[tuple[str, list[str]]]] = {}

    for layer, directions in DDD_NAMING_REGISTRY.items():
        for direction, types in directions.items():
            # Create a descriptive group name (e.g., "ADAPTERS (DRIVING)")
            group_suffix = (
                f" ({direction})"
                if direction not in (DirectionEnum.NONE, DirectionEnum.ANY)
                else ""
            )
            group_name = f"{layer}{group_suffix}".upper()

            if group_name not in grouped_display:
                grouped_display[group_name] = []

            for comp_type, regex_list in types.items():
                type_name = comp_type.name
                grouped_display[group_name].append((type_name, regex_list))

    # 2. Build HTML Content
    html_parts = []
    html_parts.append(f'<div style="{TXT_STYLE}">')
    html_parts.append(f'<h3 style="{H3_STYLE}">🧩 Architectural Naming Protocols</h3>')
    html_parts.append(
        '<div style="font-style:italic; margin-bottom:8px; color:#666;">'
        "Strict Full Match rules enforced by SRM v2.0 engine."
        "</div>"
    )

    # Defined order for visual stability
    display_order = [
        "COMPOSITION",
        "DOMAIN",
        "APP",
        "PORTS (DRIVING)",
        "PORTS (DRIVEN)",
        "PORTS",
        "ADAPTERS (DRIVING)",
        "ADAPTERS (DRIVEN)",
        "ADAPTERS",
        "GLOBAL",
    ]

    for group_key in display_order:
        items = grouped_display.get(group_key)
        if not items:
            continue

        html_parts.append(
            '<div style="margin-bottom: 8px; border-left: 3px solid #eee; padding-left: 6px;">'
        )
        html_parts.append(
            f'<div style="font-weight:bold; color:#2C3E50; font-size:12px; margin-bottom:2px;">{group_key}</div>'
        )

        # Sort items by type name for readability
        for type_name, tokens in sorted(items):
            # Format regex patterns as clean blue tags
            tags_str = " ".join([f'<span style="{TAG_STYLE}">{t}</span>' for t in tokens])

            html_parts.append('<div style="margin-left: 2px; margin-bottom: 2px;">')
            html_parts.append(f'<span style="{TYPE_HEADER_STYLE}">{type_name}:</span> {tags_str}')
            html_parts.append("</div>")

        html_parts.append("</div>")

    html_parts.append("</div>")
    return "".join(html_parts)
