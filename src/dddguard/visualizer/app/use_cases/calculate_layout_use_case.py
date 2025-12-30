from typing import List, NamedTuple
from collections import defaultdict
from dataclasses import dataclass, replace, field

from dddguard.shared import ArchetypeType

from ...domain import (
    DependencyGraph,
    ContextTower,
    TowerZone,
    ZoneBackground,
    StyleService,
    ZoneBuilderService,
    VisualContainer,
    FlowPackingService,
)

from ..workflows.find_optimized_tower_workflow import FindOptimizedTowerWorkflow


class ZoneLayoutData(NamedTuple):
    name: str
    y_start: float
    height: float
    width: float
    items: List[VisualContainer] 
    backgrounds: List[ZoneBackground]


@dataclass(frozen=True, kw_only=True, slots=True)
class CalculateLayoutUseCase:
    """
    App Use Case: Orchestrates the calculation of the visual layout.
    Supports both Single-Column zones (App/Domain) and Split-Column zones (Adapters/Ports).
    """

    style: StyleService
    builder: ZoneBuilderService
    optimize_tower: FindOptimizedTowerWorkflow
    packer: FlowPackingService = field(default_factory=FlowPackingService)

    def execute(
        self, graph: DependencyGraph,
    ) -> List[ContextTower]:
        nodes_by_context = defaultdict(list)

        # 1. Global Filter Loop
        for node in graph.all_nodes:
            if node.is_external:
                continue
            
            if node.component_type == ArchetypeType.MARKER or str(node.component_type) == "MARKER":
                continue

            nodes_by_context[node.context].append(node)

        towers = []
        curr_x = 0.0

        for ctx_name, nodes in sorted(nodes_by_context.items()):
            if not nodes:
                continue

            # 2. Create tower geometry
            tower = self._create_tower_geometry(ctx_name, nodes)

            # 3. Position the tower
            tower = replace(tower, x=curr_x)
            towers.append(tower)

            curr_x += tower.width + self.style.TOWER_PAD_X

        return towers

    def _create_tower_geometry(self, name: str, nodes: list) -> ContextTower:
        # 1. Build Initial Structure (ZoneKey -> List[Container])
        structure = self.builder.build_context_structure(nodes)

        # 2. Apply Optimization Workflow (Reorders the lists independently)
        structure = self.optimize_tower.execute(structure)

        # Architectural Zone Order
        zone_order = ["ADAPTERS", "PORTS", "APP", "DOMAIN", "COMPOSITION", "OTHER"]
        
        zone_layouts: List[ZoneLayoutData] = []
        current_y = self.style.HEADER_HEIGHT
        
        # Track max width found across all zones to align backgrounds later
        max_tower_width = self.style.MIN_BLOCK_WIDTH

        for z_name in zone_order:
            # For ADAPTERS/PORTS, we check for suffixed keys.
            # For others, we check exact match.
            is_split_zone = z_name in ("ADAPTERS", "PORTS")
            
            if is_split_zone:
                driving = structure.get(f"{z_name}_DRIVING", [])
                driven = structure.get(f"{z_name}_DRIVEN", [])
                other = structure.get(f"{z_name}_OTHER", [])
                has_content = bool(driving or driven or other)
            else:
                items = structure.get(z_name, [])
                has_content = bool(items)

            if not has_content:
                continue

            zone_bg_y = current_y
            
            # --- RENDER LOGIC ---
            
            if is_split_zone:
                # SPLIT LAYOUT: Other on Top, then Split Driving/Driven
                layout_res = self._layout_split_zone(
                    z_name=z_name, 
                    driving=driving, 
                    driven=driven, 
                    other=other, 
                    start_y=current_y
                )
            else:
                # NORMAL LAYOUT: Single Flow
                layout_res = self._layout_single_zone(
                    z_name=z_name, 
                    items=items, 
                    start_y=current_y
                )

            # Update geometry tracking
            max_tower_width = max(max_tower_width, layout_res.width)
            current_y = zone_bg_y + layout_res.height + self.style.ZONE_GAP_Y

            zone_layouts.append(layout_res)

        final_zones: List[TowerZone] = []

        # 3. Finalize Backgrounds (Stretch to max width)
        for z in zone_layouts:
            final_backgrounds = []
            
            # Re-process backgrounds to match global tower width
            for bg in z.backgrounds:
                # Split Logic Alignment
                if bg.side == "left":
                    # Stays on left
                    final_backgrounds.append(bg)
                elif bg.side == "right":
                    # Moves to far right
                    new_x = max_tower_width - bg.width
                    
                    final_backgrounds.append(replace(bg, x_rel=new_x))
                else: # Center
                    # Stretch to full width
                    full_w = max_tower_width - self.style.ZONE_HEADER_WIDTH
                    final_backgrounds.append(replace(bg, width=full_w))

            # Re-position items if needed (e.g. centering single zones, or right-aligning driven)
            final_items = []
            for it in z.items:
                final_items.append(it)

            
            # If we have distinct Left/Right backgrounds, we should fill the gap.
            has_left = any(b.side == "left" for b in final_backgrounds)
            has_right = any(b.side == "right" for b in final_backgrounds)
            
            if has_left and has_right:
                # Find the right-side bg
                rbg = next(b for b in final_backgrounds if b.side == "right")
                lbg = next(b for b in final_backgrounds if b.side == "left")
                
                # If there is a gap between left end and right start
                gap = rbg.x_rel - (lbg.x_rel + lbg.width)
                if gap > 0:
                    # Extend Left to cover it? Or split?
                    # Let's extend Left
                    lbg_idx = final_backgrounds.index(lbg)
                    final_backgrounds[lbg_idx] = replace(lbg, width=lbg.width + gap)

            final_zones.append(
                TowerZone(
                    name=z.name,
                    y_bottom=z.y_start + z.height,
                    height=z.height,
                    backgrounds=final_backgrounds,
                    containers=final_items,
                )
            )

        return ContextTower(
            name=name,
            x=0.0,
            width=max_tower_width,
            zones=final_zones,
            forced_height=current_y,
        )

    def _layout_single_zone(self, z_name: str, items: List[VisualContainer], start_y: float) -> ZoneLayoutData:
        start_x = self.style.ZONE_HEADER_WIDTH
        
        packed = self.packer.pack(
            elements=items,
            start_x=start_x,
            start_y=start_y,
            gap_x=self.style.CONTAINER_GAP_X,
            gap_y=self.style.CONTAINER_GAP_Y,
            wrap_width=None
        )
        
        w = packed.max_right
        h = packed.max_bottom - start_y
        
        bg = ZoneBackground(
            x_rel=self.style.ZONE_HEADER_WIDTH,
            y_rel=start_y,
            width=max(0.0, w - self.style.ZONE_HEADER_WIDTH),
            height=h,
            color=self.style.ZONE_BG_COLORS.get(f"{z_name}_BG", "#f0f0f0"),
            side="center"
        )
        
        return ZoneLayoutData(
            name=z_name,
            y_start=start_y,
            height=h,
            width=w,
            items=packed.positioned,
            backgrounds=[bg]
        )

    def _layout_split_zone(
        self, z_name: str, driving: List, driven: List, other: List, start_y: float
    ) -> ZoneLayoutData:
        """
        Layouts Other on top, then Driving (Left) and Driven (Right).
        """
        current_y = start_y
        all_items = []
        backgrounds = []
        
        max_w = self.style.ZONE_HEADER_WIDTH
        
        # 1. Other (Full Width)
        if other:
            packed_other = self.packer.pack(
                elements=other,
                start_x=self.style.ZONE_HEADER_WIDTH,
                start_y=current_y,
                gap_x=self.style.CONTAINER_GAP_X,
                gap_y=self.style.CONTAINER_GAP_Y,
                wrap_width=None
            )
            all_items.extend(packed_other.positioned)
            
            h_other = packed_other.max_bottom - current_y
            w_other = packed_other.max_right
            
            backgrounds.append(
                ZoneBackground(
                    x_rel=self.style.ZONE_HEADER_WIDTH,
                    y_rel=current_y,
                    width=max(0.0, w_other - self.style.ZONE_HEADER_WIDTH),
                    height=h_other,
                    color=self.style.ZONE_BG_COLORS.get(f"{z_name}_BG", "#f0f0f0"),
                    side="center"
                )
            )
            
            current_y = packed_other.max_bottom + self.style.ROW_GAP_Y
            max_w = max(max_w, w_other)

        # 2. Split Columns (Driving vs Driven)
        # We need to pack them independently to determine widths, then place Driven to the right of Driving.
        
        start_x_driving = self.style.ZONE_HEADER_WIDTH
        
        # Reserve distinct label space?
        # Let's add a small top pad if we have split columns for the "Driving/Driven" label
        split_start_y = current_y + self.style.SPLIT_LABEL_HEIGHT
        
        packed_driving = self.packer.pack(
            elements=driving,
            start_x=start_x_driving,
            start_y=split_start_y,
            gap_x=self.style.CONTAINER_GAP_X,
            gap_y=self.style.CONTAINER_GAP_Y,
            wrap_width=None
        )
        
        w_driving = max(self.style.MIN_BLOCK_WIDTH, packed_driving.max_right - start_x_driving)
        # Gap between columns
        col_gap = self.style.MIN_BLOCK_WIDTH * 0.5 
        
        start_x_driven = packed_driving.max_right + col_gap
        
        packed_driven = self.packer.pack(
            elements=driven,
            start_x=start_x_driven,
            start_y=split_start_y,
            gap_x=self.style.CONTAINER_GAP_X,
            gap_y=self.style.CONTAINER_GAP_Y,
            wrap_width=None
        )
        
        w_driven = packed_driven.max_right - start_x_driven
        
        # Combine items
        all_items.extend(packed_driving.positioned)
        all_items.extend(packed_driven.positioned)
        
        split_bottom = max(packed_driving.max_bottom, packed_driven.max_bottom, split_start_y + 1.0)
        split_height = split_bottom - current_y # Include the label pad
        
        # Driving Background
        backgrounds.append(
            ZoneBackground(
                x_rel=start_x_driving,
                y_rel=current_y, # Start at current_y to cover label area
                width=w_driving,
                height=split_height,
                color=self.style.ZONE_BG_COLORS.get(f"{z_name}_DRIVING_BG", "#e8f5e9"),
                side="left",
                label="DRIVING"
            )
        )
        
        # Driven Background
        backgrounds.append(
            ZoneBackground(
                x_rel=start_x_driven,
                y_rel=current_y,
                width=w_driven,
                height=split_height,
                color=self.style.ZONE_BG_COLORS.get(f"{z_name}_DRIVEN_BG", "#fffde7"),
                side="right",
                label="DRIVEN"
            )
        )
        
        max_w = max(max_w, packed_driven.max_right)
        total_height = split_bottom - start_y
        
        return ZoneLayoutData(
            name=z_name,
            y_start=start_y,
            height=total_height,
            width=max_w,
            items=all_items,
            backgrounds=backgrounds
        )