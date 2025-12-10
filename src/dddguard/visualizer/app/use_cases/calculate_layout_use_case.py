from typing import List, Dict
from collections import defaultdict
from dataclasses import dataclass, replace

from dddguard.scanner.domain import DependencyGraph

from ...domain import (
    ContextTower, TowerZone, Box, ZoneBackground, 
    StyleService, ZoneBuilderService, HorizontalAligner, VerticalStacker
)


@dataclass(frozen=True, kw_only=True, slots=True)
class CalculateLayoutUseCase:
    """
    App Use Case: Orchestrates the calculation of the visual layout.
    """
    style: StyleService
    builder: ZoneBuilderService
    aligner: HorizontalAligner
    stacker: VerticalStacker

    def execute(self, graph: DependencyGraph) -> List[ContextTower]:
        nodes_by_context = defaultdict(list)
        for node in graph.all_nodes:
            if not node.is_external:
                nodes_by_context[node.context].append(node)

        towers = []
        curr_x = 0.0
        
        # Sort contexts for diagram stability
        for ctx_name, nodes in sorted(nodes_by_context.items()):
            if not nodes: continue
            
            # 1. Create tower geometry (the entire structure and zones)
            tower = self._create_tower_geometry(ctx_name, nodes)
            
            # 2. Position the tower globally on the canvas
            tower = replace(tower, x=curr_x)
            towers.append(tower)
            
            curr_x += tower.width + self.style.TOWER_PAD_X

        return towers

    def _create_tower_geometry(self, name: str, nodes: list) -> ContextTower:
        # A. Build the raw structure (Layer -> Row -> Alignment)
        structure = self.builder.build_context_structure(nodes)
        
        # B. Phase 1: Horizontal alignment (Adapters <-> Interfaces)
        # Get the smart width of the right column and interface offsets
        smart_r_width, if_positions = self.aligner.calculate_offsets(structure)
        
        # C. Calculate column widths (Left, Center, Right)
        geo = self._calc_dimensions(structure, smart_r_width)
        
        # D. Phase 2 & 3: Assembling zones
        zones = []
        current_y = self.style.HEADER_HEIGHT
        
        # Zone drawing order
        zone_order = ["PORTS", "ADAPTERS", "APP", "DOMAIN", "COMPOSITION"]
        
        for z_name in zone_order:
            zone_start_y = current_y
            
            # === SPECIAL LOGIC: APP LAYER (Vertical Gravity) ===
            if z_name == "APP":
                app_nodes, app_height = self.stacker.layout_app_layer(
                    structure.get("APP", {}),
                    if_positions,
                    {
                        "col_l": geo["col_l_x"], "col_r": geo["col_r_x"],
                        "sidebar": geo["sidebar_w"], "content_w": geo["final_content_w"],
                        "start_y": current_y
                    },
                    self._make_box # Pass the box factory as a callback
                )
                bg = ZoneBackground(
                    x_rel=geo["sidebar_w"], y_rel=zone_start_y, 
                    width=geo["final_content_w"], height=app_height,
                    color=self.style.ZONE_BG_COLORS.get("APP_BG", "#f5f5f5"), side="center"
                )
                zones.append(TowerZone(
                    name=z_name, y_bottom=current_y + app_height, height=app_height,
                    backgrounds=[bg], nodes=app_nodes
                ))
                current_y += app_height + self.style.ZONE_GAP_Y
                continue
            
            # === STANDARD LOGIC (Simple Flow) ===
            zone_nodes, zone_height = self._layout_standard_zone(z_name, structure.get(z_name, {}), current_y, geo)
            
            backgrounds = self._create_backgrounds(z_name, zone_start_y, zone_height, geo)
            
            zones.append(TowerZone(
                name=z_name, y_bottom=current_y + zone_height, height=zone_height,
                backgrounds=backgrounds, nodes=zone_nodes
            ))
            current_y += zone_height + self.style.ZONE_GAP_Y

        return ContextTower(name=name, x=0, width=geo["total_w"], zones=zones, forced_height=current_y)

    # --- Helpers ---

    def _calc_dimensions(self, structure: Dict, smart_r: float) -> Dict[str, float]:
        # 1. Calculate maximum content widths
        ml, mc, mr = 0.0, self.style.MIN_NODE_WIDTH * 2, smart_r
        for z, rows in structure.items():
            if z == "APP": continue # APP is calculated dynamically
            for _, sides in rows.items():
                if sides["center"]: 
                    mc = max(mc, self.builder.sum_width(sides["center"]))
                else:
                    ml = max(ml, self.builder.sum_width(sides["left"]))
                    mr = max(mr, self.builder.sum_width(sides["right"]))
        
        # 2. Add block indents
        req_l = ml + (self.style.BLOCK_PAD_X * 2)
        req_r = mr + (self.style.BLOCK_PAD_X * 2)
        
        fl = max(req_l, self.style.MIN_BLOCK_WIDTH)
        fr = max(req_r, self.style.MIN_BLOCK_WIDTH)
        
        # 3. Synchronize the central width
        split_w = fl + fr + self.style.SPLIT_GAP_X
        final_w = max(split_w, mc + (self.style.NODE_GAP_X * 2))
        
        if final_w > split_w:
            diff = (final_w - split_w) / 2
            fl += diff; fr += diff
            
        sb_w = self.style.ZONE_HEADER_WIDTH
        
        return {
            "final_col_l": fl, "final_col_r": fr,
            "final_content_w": final_w,
            "col_l_x": sb_w,
            "col_r_x": sb_w + fl + self.style.SPLIT_GAP_X,
            "sidebar_w": sb_w,
            "total_w": sb_w + final_w
        }

    def _layout_standard_zone(self, z_name, rows_dict, start_y, geo):
        nodes = []
        curr_y = start_y
        
        if not rows_dict:
             return nodes, self.style.NODE_HEIGHT + self.style.ROW_PAD_Y
        
        for r_idx in sorted(rows_dict.keys()):
            sides = rows_dict[r_idx]
            h = self.style.NODE_HEIGHT + self.style.ROW_PAD_Y * 2
            
            # Center Flow
            if sides["center"]:
                wc = self.builder.sum_width(sides["center"])
                cx = geo["sidebar_w"] + (geo["final_content_w"] - wc)/2
                for b in sides["center"]:
                    nodes.append(self._make_box(cx, curr_y, b))
                    cx += b["width"] + self.style.NODE_GAP_X
            else:
                # Left Flow
                w_l = self.builder.sum_width(sides["left"])
                offset_l = (geo["final_col_l"] - w_l) / 2
                curr_x = geo["col_l_x"] + max(0, offset_l)
                for b in sides["left"]:
                    nodes.append(self._make_box(curr_x, curr_y, b))
                    curr_x += b["width"] + self.style.NODE_GAP_X
                
                # Right Flow (Support Smart Offset from Phase 1)
                w_r = self.builder.sum_width(sides["right"])
                offset_r = (geo["final_col_r"] - w_r) / 2
                curr_x_r = geo["col_r_x"] + max(0, offset_r)
                for b in sides["right"]:
                    if "_smart_offset" in b:
                        pos = geo["col_r_x"] + self.style.BLOCK_PAD_X + b["_smart_offset"]
                    else:
                        pos = curr_x_r
                        curr_x_r += b["width"] + self.style.NODE_GAP_X
                    nodes.append(self._make_box(pos, curr_y, b))
            
            curr_y += h
            
        return nodes, curr_y - start_y

    def _create_backgrounds(self, z_name, start_y, height, geo):
        if z_name in ["PORTS", "ADAPTERS"]:
            return [
                ZoneBackground(x_rel=geo["col_l_x"], y_rel=start_y, width=geo["final_col_l"], height=height, 
                               color=self.style.ZONE_BG_COLORS["DRIVING_BG"], label="DRIVING", label_align="center", side="left"),
                ZoneBackground(x_rel=geo["col_r_x"], y_rel=start_y, width=geo["final_col_r"], height=height, 
                               color=self.style.ZONE_BG_COLORS["DRIVEN_BG"], label="DRIVEN", label_align="center", side="right")
            ]
        bg_color = self.style.ZONE_BG_COLORS.get(f"{z_name}_BG", "#f5f5f5")
        return [ZoneBackground(x_rel=geo["sidebar_w"], y_rel=start_y, width=geo["final_content_w"], height=height, 
                               color=bg_color, label=None, label_align="center", side="center")]

    def _make_box(self, x: float, y: float, node_data: dict) -> Box:
        return Box(
            x=x, y=y + self.style.ROW_PAD_Y,
            width=node_data["width"], height=node_data["height"],
            label=node_data["label"], color=node_data["color"],
            id=node_data["id"], layer=node_data["layer"],
            raw_type=node_data["raw_type"], context=node_data.get("context", ""),
            outgoing_imports=node_data["imports"],
        )