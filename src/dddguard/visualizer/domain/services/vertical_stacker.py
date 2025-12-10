from dataclasses import dataclass
from typing import Dict, List, Tuple, Callable, Any
import statistics

from ...domain import Box
from .styling.style_service import StyleService


@dataclass(frozen=True, kw_only=True, slots=True)
class VerticalStacker:
    """
    Domain Service: Strategy for Vertical Layout (Gravity & Tetris).
    Calculates positions for the APP layer to stack Use Cases under dependencies.
    """
    style: StyleService

    def layout_app_layer(
        self, 
        app_rows: Dict[str, Any], 
        if_offsets: Dict[str, float], 
        coords: Dict[str, float], 
        make_box_fn: Callable 
    ) -> Tuple[List[Box], float]:
        
        final_nodes = []
        col_l_x = coords["col_l"]
        col_r_x = coords["col_r"]
        start_y = coords["start_y"]
        
        # --- 1. Fixed Nodes (Interfaces) ---
        interfaces = app_rows.get(0, {}).get("right", [])
        handlers = app_rows.get(0, {}).get("left", []) 
        
        rel_y = self.style.ROW_PAD_Y 
        
        for node in interfaces:
            x_pos = col_r_x + self.style.BLOCK_PAD_X + node.get("_smart_offset", 0.0)
            final_nodes.append(make_box_fn(x_pos, start_y + rel_y, node))

        curr_h_x = col_l_x
        for node in handlers:
            final_nodes.append(make_box_fn(curr_h_x, start_y + rel_y, node))
            curr_h_x += node["width"] + self.style.NODE_GAP_X

        rel_y += self.style.NODE_HEIGHT + (self.style.ROW_PAD_Y * 2)

        # --- 2. Dynamic Nodes (Use Cases) ---
        use_cases = []
        use_cases.extend(app_rows.get(2, {}).get("left", [])) 
        use_cases.extend(app_rows.get(2, {}).get("right", []))
        use_cases.extend(app_rows.get(1, {}).get("center", [])) 

        if not use_cases:
            return final_nodes, rel_y

        # --- 3. Gravity ---
        uc_placement = []
        for uc in use_cases:
            targets_x = []
            for link in uc["imports"]:
                tid = link["module"]
                if tid in if_offsets:
                    if_node = next((n for n in interfaces if n["id"] == tid), None)
                    w = if_node["width"] if if_node else 0
                    center = col_r_x + self.style.BLOCK_PAD_X + if_offsets[tid] + (w/2)
                    targets_x.append(center)
            
            if targets_x:
                gravity = statistics.mean(targets_x) - (uc["width"] / 2)
            else:
                gravity = col_l_x 
            
            uc_placement.append({"node": uc, "x": gravity})

        # --- 4. Tetris Drop ---
        uc_placement.sort(key=lambda p: p["x"])
        placed_boxes = []
        row_height = self.style.NODE_HEIGHT
        gap_y = self.style.NODE_GAP_Y
        
        for item in uc_placement:
            uc = item["node"]
            ideal_x = item["x"]
            
            min_x = coords["sidebar"]
            max_x = coords["sidebar"] + coords["content_w"] - uc["width"]
            ideal_x = max(min_x, min(max_x, ideal_x))

            test_y = rel_y
            while True:
                collision = False
                margin = self.style.NODE_GAP_X / 2 
                
                for px, py, pw, ph in placed_boxes:
                    if (ideal_x < px + pw + margin and 
                        ideal_x + uc["width"] + margin > px and
                        test_y < py + ph + gap_y and 
                        test_y + row_height + gap_y > py):
                        collision = True
                        break
                
                if not collision: break
                test_y += row_height + gap_y
            
            final_nodes.append(make_box_fn(ideal_x, start_y + test_y - self.style.ROW_PAD_Y, uc))
            placed_boxes.append((ideal_x, test_y, uc["width"], row_height))

        # --- 5. Height ---
        max_y = rel_y
        for _, py, _, ph in placed_boxes:
            max_y = max(max_y, py + ph)
        
        return final_nodes, max_y + self.style.ROW_PAD_Y