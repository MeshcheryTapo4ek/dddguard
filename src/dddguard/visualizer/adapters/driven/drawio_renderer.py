import uuid
import html
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Tuple
from xml.dom import minidom

from dddguard.shared import ContextLayerEnum
from dddguard.shared.assets import get_architecture_legend, get_naming_cloud_html

from ...app import IDiagramRenderer

from ...domain import (
    ContextTower, 
    Box, 
    StyleService, 
    EdgeColorService, 
    EdgeRoutingService
)

from .errors import FileWriteError


@dataclass(frozen=True, kw_only=True, slots=True)
class DrawioRenderer(IDiagramRenderer):
    """
    Driven adapter: renders context towers as Draw.io XML.
    Uses Domain Services (Styling) to determine look & feel.
    """
    style: StyleService = field(default_factory=StyleService)
    color_service: EdgeColorService = field(default_factory=EdgeColorService)
    routing_service: EdgeRoutingService = field(default_factory=EdgeRoutingService)
    
    # Configuration
    SCALE: int = 40
    README_WIDTH: int = 16
    README_PADDING: int = 2

    def render(self, towers: List[ContextTower], output_path: Path) -> None:
        if not towers:
            return

        try:
            # 1. Setup XML Structure
            mxfile = ET.Element("mxfile", host="Electron", agent="DDDGuard", type="device")
            diagram = ET.SubElement(mxfile, "diagram", id=str(uuid.uuid4()), name="Architecture")

            mxGraphModel = ET.SubElement(
                diagram,
                "mxGraphModel",
                dx="0", dy="0", grid="1", gridSize="10",
                guides="1", tooltips="1", connect="1", arrows="1",
                fold="1", page="1", pageScale="1",
                pageWidth="1169", pageHeight="827",
                math="0", shadow="0",
            )
            mxGraphModel.set("background", "#FFFFFF")

            root = ET.SubElement(mxGraphModel, "root")
            ET.SubElement(root, "mxCell", id="0")
            ET.SubElement(root, "mxCell", id="1", parent="0")

            # 2. Render Sidebar (Legend + Naming Cloud)
            self._render_sidebar(root, towers)

            # Offset content to the right of the sidebar
            x_offset = self.README_WIDTH + self.README_PADDING

            node_xml_ids: Dict[str, str] = {}
            nodes_by_id: Dict[str, Box] = {}
            node_geometries: Dict[str, Tuple[float, float, float, float]] = {}
            all_nodes_flat: List[Tuple[ContextTower, Box]] = []

            # 3. Render Containers & Backgrounds
            for tower in towers:
                tower_x = tower.x + x_offset
                container_id = self._add_context_container(
                    root,
                    label=f"{tower.name.upper()} CONTEXT",
                    x=tower_x, y=0.0, w=tower.width, h=tower.forced_height,
                )

                for zone in tower.zones:
                    # Side Label (e.g. "DOMAIN")
                    self._add_side_label(
                        root, parent_id=container_id, label=zone.name,
                        x=0.0, y=zone.backgrounds[0].y_rel if zone.backgrounds else 0.0,
                        w=self.style.ZONE_HEADER_WIDTH, h=zone.height,
                    )
                    # Colored Backgrounds
                    for bg in zone.backgrounds:
                        self._add_zone_bg(
                            root, parent_id=container_id,
                            x=bg.x_rel, y=bg.y_rel, w=bg.width, h=bg.height,
                            color=bg.color, label=bg.label,
                        )
                    # Collect nodes for later processing
                    for node in zone.nodes:
                        all_nodes_flat.append((tower, node))
                        if node.id:
                            nodes_by_id[node.id] = node

            # 4. Render Nodes (Vertices)
            for tower, node in all_nodes_flat:
                abs_x = (tower.x + x_offset) + node.x
                abs_y = node.y
                
                xml_id = self._add_vertex(
                    root,
                    label=self._format_node_label(node.label, node.raw_type),
                    x=abs_x, y=abs_y, w=node.width, h=node.height,
                    fill_color=node.color,
                    dashed="1" if "Interface" in node.raw_type else "0",
                )
                
                if node.id:
                    node_xml_ids[node.id] = xml_id
                    node_geometries[node.id] = (abs_x, abs_y, node.width, node.height)

            # 5. Render Edges
            only_boxes = [n for _, n in all_nodes_flat]
            self._render_edges(root, only_boxes, node_xml_ids, nodes_by_id, node_geometries)

            # 6. Save File
            xml_str = minidom.parseString(ET.tostring(mxfile)).toprettyxml(indent="  ")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(xml_str)

        except IOError as e:
            raise FileWriteError(str(output_path), str(e))
        except Exception:
            raise

    # --- SIDEBAR GENERATION ---
    def _render_sidebar(self, root, towers: List[ContextTower]) -> None:
        """
        Renders the static Legend and the dynamic Naming Cloud side-by-side or stacked.
        Here we stack them vertically in the left column.
        """
        context_names = [t.name for t in towers]
        
        # A. Static Legend Block
        legend_html = get_architecture_legend(context_names)
        # Estimate height: Header + Macro + Guide + Layers (approx 24 grid units)
        legend_h = 24.0 
        
        self._add_text_block(
            root, 
            id_suffix="legend", 
            html_content=legend_html, 
            x=0, y=0, 
            w=self.README_WIDTH, h=legend_h
        )

        # B. Dynamic Naming Block (Placed below Legend)
        naming_html = get_naming_cloud_html()
        naming_y = legend_h + 0.5 # Small gap
        naming_h = 24.0 
        
        self._add_text_block(
            root, 
            id_suffix="naming", 
            html_content=naming_html, 
            x=0, y=naming_y, 
            w=self.README_WIDTH, h=naming_h
        )

    def _add_text_block(self, root, id_suffix: str, html_content: str, x: float, y: float, w: float, h: float):
        """Generic helper to add an HTML text box."""
        uid = str(uuid.uuid4())
        # Draw.io style for HTML label
        style = (
            "text;html=1;whiteSpace=wrap;overflow=hidden;rounded=1;"
            "strokeColor=#b0bec5;fillColor=#fcfcfc;spacing=10;"
            "verticalAlign=top;align=left;"
        )
        cell = ET.SubElement(root, "mxCell", id=uid, value=html_content, style=style, parent="1", vertex="1")
        ET.SubElement(cell, "mxGeometry", 
            x=str(x * self.SCALE), 
            y=str(y * self.SCALE), 
            width=str(w * self.SCALE), 
            height=str(h * self.SCALE)
        ).set("as", "geometry")

    # --- GRAPH ELEMENT HELPERS ---

    def _add_context_container(self, root, label: str, x: float, y: float, w: float, h: float) -> str:
        uid = str(uuid.uuid4())
        style = (
            "swimlane;whiteSpace=wrap;html=1;startSize=30;"
            "fillColor=#FFFFFF;strokeColor=#000000;"
            "fontStyle=1;fontSize=16;verticalAlign=top;fontColor=#000000;"
            "collapsible=1;container=1;recursiveResize=1;" 
        )
        cell = ET.SubElement(root, "mxCell", id=uid, value=label, style=style, parent="1", vertex="1")
        ET.SubElement(cell, "mxGeometry", 
            x=str(x * self.SCALE), 
            y=str(y * self.SCALE), 
            width=str(w * self.SCALE), 
            height=str(h * self.SCALE)
        ).set("as", "geometry")
        return uid

    def _add_zone_bg(self, root, parent_id: str, x: float, y: float, w: float, h: float, color: str, label: str | None) -> None:
        uid = str(uuid.uuid4())
        # Helper text style for zone label
        style = (
            f"rounded=1;whiteSpace=wrap;html=1;fillColor={color};strokeColor=none;"
            "pointerEvents=0;arcSize=4;verticalAlign=top;align=center;"
            "fontStyle=1;fontColor=#666666;fontSize=12;spacingTop=4;"
        )
        cell = ET.SubElement(root, "mxCell", id=uid, value=label if label else "", style=style, parent=parent_id, vertex="1")
        ET.SubElement(cell, "mxGeometry", 
            x=str(x * self.SCALE), 
            y=str(y * self.SCALE), 
            width=str(w * self.SCALE), 
            height=str(h * self.SCALE)
        ).set("as", "geometry")

    def _add_side_label(self, root, parent_id: str, label: str, x: float, y: float, w: float, h: float) -> None:
        uid = str(uuid.uuid4())
        style = (
            "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;"
            "whiteSpace=wrap;rounded=0;fontColor=#333333;fontStyle=1;fontSize=13;fontFamily=Helvetica;"
        )
        cell = ET.SubElement(root, "mxCell", id=uid, value=label, style=style, parent=parent_id, vertex="1")
        ET.SubElement(cell, "mxGeometry", 
            x=str(x * self.SCALE), 
            y=str(y * self.SCALE), 
            width=str(w * self.SCALE), 
            height=str(h * self.SCALE)
        ).set("as", "geometry")

    def _add_vertex(self, root, label: str, x: float, y: float, w: float, h: float, fill_color: str, dashed: str) -> str:
        uid = str(uuid.uuid4())
        style = (
            f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill_color};strokeColor=#666666;"
            f"fontColor=#000000;dashed={dashed};shadow=0;fontSize=14;"
        )
        cell = ET.SubElement(root, "mxCell", id=uid, value=label, style=style, parent="1", vertex="1")
        ET.SubElement(cell, "mxGeometry", 
            x=str(x * self.SCALE), 
            y=str(y * self.SCALE), 
            width=str(w * self.SCALE), 
            height=str(h * self.SCALE)
        ).set("as", "geometry")
        return uid

    def _format_node_label(self, label: str, type_str: str) -> str:
        return (
            f'<div style="line-height:1.2;">'
            f'<b style="font-size:15px;">{html.escape(label)}</b><br>'
            f'<span style="font-size:12px;color:#444;">&lt;{html.escape(type_str)}&gt;</span>'
            f'</div>'
        )

    # --- EDGE ROUTING LOGIC ---

    def _render_edges(
        self,
        root,
        all_boxes: List[Box],
        node_map: Dict[str, str],
        nodes_by_id: Dict[str, Box],
        geometries: Dict[str, Tuple[float, float, float, float]],
    ) -> None:
        """
        Renders edges with coloring and intelligent anchor routing.
        """
        base_edge_style = (
            "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;"
            "html=1;strokeWidth=2;endArrow=classic;endSize=8;jumpStyle=arc;jumpSize=6;"
        )

        raw_edges: List[Tuple[str, str]] = []

        # 1. Filter and Collect Edges
        for source_box in all_boxes:
            if not source_box.id or source_box.id not in node_map: continue
            
            # Filter: No arrows FROM Composition
            if source_box.layer == ContextLayerEnum.COMPOSITION: continue

            # Filter: No arrows FROM Errors
            if "Error" in source_box.raw_type or "Exception" in source_box.raw_type:
                continue

            for imp in source_box.outgoing_imports:
                target_id = imp["module"]
                if target_id not in node_map or target_id == source_box.id: continue
                
                target_node = nodes_by_id.get(target_id)
                if not self._should_draw_edge(target_node): continue
                
                raw_edges.append((source_box.id, target_id))

        # 2. Build Dependency Maps for Sorting
        outgoing_map: Dict[str, List[str]] = defaultdict(list)
        incoming_map: Dict[str, List[str]] = defaultdict(list)

        for src, tgt in raw_edges:
            outgoing_map[src].append(tgt)
            incoming_map[tgt].append(src)

        # Sort targets by X coordinate (Left -> Right)
        for src, targets in outgoing_map.items():
            targets.sort(key=lambda t_id: geometries.get(t_id, (0,0,0,0))[0])

        # Sort sources by X coordinate
        for tgt, sources in incoming_map.items():
            sources.sort(key=lambda s_id: geometries.get(s_id, (0,0,0,0))[0])

        # 3. Group by Context for Color Consistency
        sources_by_context: Dict[str, List[str]] = defaultdict(list)
        for src_id in outgoing_map.keys():
            box = nodes_by_id.get(src_id)
            ctx = box.context if box else "unknown"
            sources_by_context[ctx].append(src_id)
        
        for ctx in sources_by_context: 
            sources_by_context[ctx].sort()

        # 4. Draw Edges
        for ctx, source_ids in sources_by_context.items():
            total_sources_in_ctx = len(source_ids)
            
            for node_idx, src_id in enumerate(source_ids):
                targets = outgoing_map[src_id]
                total_out = len(targets)
                if total_out == 0: continue

                for out_idx, target_id in enumerate(targets):
                    src_geo = geometries.get(src_id)
                    tgt_geo = geometries.get(target_id)
                    
                    # A. Determine Color
                    color = self.color_service.get_color_for_source(
                        node_idx, total_sources_in_ctx, 
                        out_idx, total_out
                    )
                    style = f"{base_edge_style}strokeColor={color};"
                    
                    # B. Determine Routing (Anchors)
                    if src_geo and tgt_geo:
                        incoming_sources = incoming_map[target_id]
                        try:
                            # 1-based index for visual balancing
                            in_idx = incoming_sources.index(src_id) + 1
                        except ValueError:
                            in_idx = 1
                        
                        in_total = len(incoming_sources)

                        style += self.routing_service.anchor_style(
                            src_geo, tgt_geo, 
                            out_idx=out_idx, out_total=total_out,
                            in_idx=in_idx, in_total=in_total
                        )
                    
                    self._create_edge(root, node_map[src_id], node_map[target_id], style)

    def _should_draw_edge(self, target_node: Box | None) -> bool:
        if target_node is None: return False
        
        # Don't draw arrows TO Composition
        if target_node.layer == ContextLayerEnum.COMPOSITION: return False
        
        # Don't draw arrows TO Errors
        if "Error" in target_node.raw_type or "Exception" in target_node.raw_type: return False

        # Only draw arrows TO Domain Services (skip Entities/VOs to reduce noise)
        if target_node.layer == ContextLayerEnum.DOMAIN:
            if target_node.raw_type != "DomainService":
                return False
        
        return True

    def _create_edge(self, root, src_id: str, tgt_id: str, style: str) -> None:
        edge_id = str(uuid.uuid4())
        cell = ET.SubElement(
            root, "mxCell", 
            id=edge_id, 
            style=style, 
            parent="1", 
            source=src_id, 
            target=tgt_id, 
            edge="1"
        )
        ET.SubElement(cell, "mxGeometry", relative="1").set("as", "geometry")