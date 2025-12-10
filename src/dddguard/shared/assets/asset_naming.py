from typing import Dict, List, Tuple

from .ddd_registry import NAMING_CONVENTIONS


def get_naming_cloud_html() -> str:
    """
    Generates dynamic HTML showing Naming Conventions (Tag Cloud).
    Shows ALL tokens without truncation.
    """
    # Styles
    H3_STYLE = "margin-top: 0; margin-bottom: 5px; color: #34495E; font-size: 14px; font-weight: bold;"
    TXT_STYLE = "font-family: Helvetica; color: #333; font-size: 11px; line-height: 1.4;"
    TAG_STYLE = (
        "display: inline-block; background-color: #EBF5FB; color: #2E86C1; "
        "padding: 1px 4px; margin: 1px; border-radius: 3px; font-size: 10px; border: 1px solid #D6EAF8;"
    )
    TYPE_HEADER_STYLE = "font-weight: bold; color: #555; margin-top: 4px; font-size: 11px;"

    # 1. Group conventions by Layer
    grouped_rules: Dict[str, List[Tuple[str, List[str]]]] = {}
    
    # Sort keys to ensure stable order
    sorted_items = sorted(NAMING_CONVENTIONS.items(), key=lambda item: (item[0][0], item[0][1]))

    for (layer, comp_type), tokens in sorted_items:
        layer_name = layer.value.upper().replace("_", " ")
        if layer_name not in grouped_rules:
            grouped_rules[layer_name] = []
        
        # Simplified type name
        type_name = comp_type.value if hasattr(comp_type, "value") else str(comp_type)
        if "." in type_name: type_name = type_name.split(".")[-1]
        
        grouped_rules[layer_name].append((type_name, tokens))

    # 2. Build HTML
    html_parts = []
    html_parts.append(f'<div style="{TXT_STYLE}">')
    html_parts.append(f'<h3 style="{H3_STYLE}">🧩 Naming Conventions</h3>')
    html_parts.append(f'<div style="font-style:italic; margin-bottom:8px; color:#666;">Auto-detected rules for this project.</div>')

    # Display Order
    layer_display_order = [
        "DOMAIN", "APP", "DRIVING ADAPTERS", "DRIVEN ADAPTERS", 
        "DRIVING PORTS", "DRIVEN PORTS", "DRIVING DTO", "DRIVEN DTO", "COMPOSITION"
    ]

    for layer_key in layer_display_order:
        items = grouped_rules.get(layer_key, [])
        if not items: continue

        html_parts.append(f'<div style="margin-bottom: 8px; border-left: 3px solid #eee; padding-left: 6px;">')
        html_parts.append(f'<div style="font-weight:bold; color:#2C3E50; font-size:12px; margin-bottom:2px;">{layer_key}</div>')
        
        for type_name, tokens in items:
            tags_str = " ".join([f'<span style="{TAG_STYLE}">{t}</span>' for t in tokens]) 
            
            html_parts.append(f'<div style="margin-left: 2px; margin-bottom: 2px;">')
            html_parts.append(f'<span style="{TYPE_HEADER_STYLE}">{type_name}:</span> {tags_str}')
            html_parts.append(f'</div>')
        
        html_parts.append(f'</div>')

    html_parts.append('</div>')
    return "".join(html_parts)