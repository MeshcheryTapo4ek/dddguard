from dataclasses import dataclass
from typing import Dict, Any, Tuple
from collections import defaultdict

from .styling.style_service import StyleService


@dataclass(frozen=True, kw_only=True, slots=True)
class HorizontalAligner:
    """
    Domain Service: Strategy for Horizontal Alignment.
    Calculates smart horizontal offsets to align Driven Adapters with Interfaces.
    """
    style: StyleService

    def calculate_offsets(self, structure: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """
        Returns: (Total Smart Width, Interface Position Map {id -> offset})
        """
        adapters_list = structure.get("ADAPTERS", {}).get(1, {}).get("right", [])
        interfaces_list = structure.get("APP", {}).get(0, {}).get("right", [])

        if not adapters_list and not interfaces_list:
            return 0.0, {}

        # 1. Build Map
        interface_map = defaultdict(list)
        interface_ids = {node["id"] for node in interfaces_list}
        orphaned_adapters = []
        
        for adapter in adapters_list:
            found_parent = False
            for link in adapter["imports"]:
                if link["module"] in interface_ids:
                    interface_map[link["module"]].append(adapter)
                    found_parent = True
                    break
            if not found_parent:
                orphaned_adapters.append(adapter)

        # 2. Create Groups
        groups = []
        for if_node in interfaces_list:
            groups.append((if_node, interface_map.get(if_node["id"], [])))
        
        if orphaned_adapters:
            groups.append((None, orphaned_adapters))

        # 3. Calculate Coordinates
        current_x = 0.0
        GAP = self.style.NODE_GAP_X
        interface_positions = {} 
        
        for if_node, adapters in groups:
            adapters.sort(key=lambda x: x["label"])
            
            adapters_w = sum(a["width"] for a in adapters) + (len(adapters) - 1) * GAP if adapters else 0.0
            if_w = if_node["width"] if if_node else 0.0
            
            group_w = max(adapters_w, if_w)
            center_x = current_x + (group_w / 2)

            if adapters:
                cursor = center_x - (adapters_w / 2)
                for adp in adapters:
                    adp["_smart_offset"] = cursor
                    cursor += adp["width"] + GAP
            
            if if_node:
                offset = center_x - (if_w / 2)
                if_node["_smart_offset"] = offset
                interface_positions[if_node["id"]] = offset

            current_x += group_w + (GAP * 2)

        return current_x, interface_positions