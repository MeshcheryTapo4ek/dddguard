import uuid
import html
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
from xml.dom import minidom

from dddguard.shared import LayerEnum, get_architecture_legend, get_naming_cloud_html

from ....app import IDiagramRenderer
from ....domain import (
    ContextTower,
    VisualElement,
    VisualContainer,
    LeafNode,
    StyleService,
    EdgeColorService,
    EdgeRoutingService,
    VisualizationOptions,
)

from .errors import FileWriteError


@dataclass(frozen=True, kw_only=True, slots=True)
class DrawioRenderer(IDiagramRenderer):
    """
    Driven adapter: renders context towers as Draw.io XML.
    Uses Domain Services (Styling) to determine look & feel.
    Supports recursive grouping (Clusters).
    """

    style: StyleService = field(default_factory=StyleService)
    color_service: EdgeColorService = field(default_factory=EdgeColorService)
    routing_service: EdgeRoutingService = field(default_factory=EdgeRoutingService)

    # Configuration
    SCALE: int = 40
    README_WIDTH: int = 16
    README_PADDING: int = 2

    def render(self, towers: List[ContextTower], output_path: Path, options: VisualizationOptions) -> None:
        if not towers:
            return

        try:
            # 1. Setup XML Structure
            mxfile = ET.Element(
                "mxfile", host="Electron", agent="DDDGuard", type="device"
            )
            diagram = ET.SubElement(
                mxfile, "diagram", id=str(uuid.uuid4()), name="Architecture"
            )

            mxGraphModel = ET.SubElement(
                diagram,
                "mxGraphModel",
                dx="0", dy="0", grid="1", gridSize="10", guides="1",
                tooltips="1", connect="1", arrows="1", fold="1", page="1",
                pageScale="1", pageWidth="1169", pageHeight="827", math="0", shadow="0",
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
            nodes_by_id: Dict[str, LeafNode] = {}
            node_geometries: Dict[str, Tuple[float, float, float, float]] = {}

            # 3. Render Containers & Backgrounds
            for tower in towers:
                tower_x = tower.x + x_offset
                container_id = self._add_context_container(
                    root,
                    label=f"{tower.name.upper()} CONTEXT",
                    x=tower_x, y=0.0,
                    w=tower.width, h=tower.forced_height,
                )

                for zone in tower.zones:
                    # Side Label (e.g. "DOMAIN")
                    self._add_side_label(
                        root,
                        parent_id=container_id,
                        label=zone.name,
                        x=0.0,
                        y=zone.backgrounds[0].y_rel if zone.backgrounds else 0.0,
                        w=self.style.ZONE_HEADER_WIDTH,
                        h=zone.height,
                    )
                    # Colored Backgrounds
                    for bg in zone.backgrounds:
                        self._add_zone_bg(
                            root,
                            parent_id=container_id,
                            x=bg.x_rel,
                            y=bg.y_rel,
                            w=bg.width,
                            h=bg.height,
                            color=bg.color,
                            label=bg.label,
                        )
                    
                    # 4. Render Nodes Recursively (handling Groups)
                    for container in zone.containers:
                        # Absolute coordinates within the Global Canvas
                        abs_x = tower_x + container.x
                        abs_y = container.y 

                        self._render_element_recursive(
                            root,
                            element=container,
                            global_x=abs_x,
                            global_y=abs_y,
                            parent_xml_id=container_id,
                            xml_ids=node_xml_ids,
                            nodes_map=nodes_by_id,
                            geometries=node_geometries,
                            parent_global_x=tower_x,
                            parent_global_y=0.0
                        )

            # 5. Render Edges
            self._render_edges(
                root, nodes_by_id, node_xml_ids, node_geometries, options
            )

            # 6. Save File
            xml_str = minidom.parseString(ET.tostring(mxfile)).toprettyxml(indent="  ")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(xml_str)

        except IOError as e:
            raise FileWriteError(str(output_path), e) from e
        except Exception:
            raise

    def _render_element_recursive(
        self,
        root,
        element: VisualElement,
        global_x: float,
        global_y: float,
        parent_xml_id: str,
        xml_ids: Dict[str, str],
        nodes_map: Dict[str, LeafNode],
        geometries: Dict[str, Tuple[float, float, float, float]],
        parent_global_x: float,
        parent_global_y: float
    ):
        """
        Polymorphic recursive renderer for VisualElement hierarchy.
        """
        rel_x = global_x - parent_global_x
        rel_y = global_y - parent_global_y
        
        if isinstance(element, VisualContainer):
            current_xml_id = parent_xml_id
            
            if element.is_visible:
                current_xml_id = self._add_group_container(
                    root, 
                    element.label, 
                    rel_x, rel_y, 
                    element.width, element.height, 
                    parent_id=parent_xml_id
                )
            
            for child in element.children:
                child_global_x = global_x + child.x
                child_global_y = global_y + child.y
                
                new_parent_gx = global_x if element.is_visible else parent_global_x
                new_parent_gy = global_y if element.is_visible else parent_global_y
                
                self._render_element_recursive(
                    root,
                    child,
                    child_global_x,
                    child_global_y,
                    current_xml_id, 
                    xml_ids,
                    nodes_map,
                    geometries,
                    parent_global_x=new_parent_gx,
                    parent_global_y=new_parent_gy
                )

        elif isinstance(element, LeafNode):
            xml_id = self._add_vertex(
                root,
                label=self._format_node_label(element.label, element.raw_type),
                x=rel_x,
                y=rel_y,
                w=element.width,
                h=element.height,
                fill_color=element.color,
                dashed="1" if "Interface" in element.raw_type else "0",
                parent_id=parent_xml_id
            )
            
            if element.id:
                xml_ids[element.id] = xml_id
                nodes_map[element.id] = element
                geometries[element.id] = (global_x, global_y, element.width, element.height)

    # --- EDGE ROUTING LOGIC ---

    def _render_edges(
        self, 
        root, 
        nodes_map: Dict[str, LeafNode], 
        xml_ids: Dict[str, str], 
        geometries: Dict[str, Tuple[float, float, float, float]],
        options: VisualizationOptions, 
    ) -> None:
        
        base_edge_style = "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;endArrow=classic;endSize=8;jumpStyle=arc;jumpSize=6;"
        
        # --- Helper for Spatial Sorting ---
        def get_node_center_x(nid: str) -> float:
            if nid in geometries:
                gx, gy, w, h = geometries[nid]
                return gx + (w / 2.0)
            return 0.0

        # --- PRE-PASS 1: Calculate Incoming Connections (Target Fanning) ---
        incoming_map = defaultdict(list)
        
        # --- PRE-PASS 2: Calculate Valid Outgoing Edges & Complexity (Source Coloring) ---
        valid_outgoing_map: Dict[str, List[str]] = defaultdict(list)
        
        for source_id, source_node in nodes_map.items():
            if self._should_skip_node(source_node, options): continue

            for imp in source_node.outgoing_imports:
                target_id = imp["module"]
                if target_id in nodes_map and target_id != source_id:
                    target_node = nodes_map[target_id]
                    if self._should_skip_node(target_node, options): continue
                    
                    if options.hide_shared_arrows and target_node.context == "shared": continue
                    
                    # It's a valid edge
                    valid_outgoing_map[source_id].append(target_id)
                    incoming_map[target_id].append(source_id)

        # SPATIAL SORTING FOR INCOMING (Solves the "X-Crossing" at entry point)
        for tid in incoming_map:
            # Sort sources by their X coordinate. 
            # Left sources get lower indices -> Enter at leftmost points.
            incoming_map[tid].sort(key=get_node_center_x)

        # Identify Complex Nodes (Spectral Waterfall Logic)
        complex_nodes = [
            sid for sid, targets in valid_outgoing_map.items() 
            if len(targets) > 1
        ]
        # Sort complex nodes based on geometry (Top-Down, Left-Right) flow for better color gradient?
        # Or just keep deterministic ID sort? 
        # Deterministic ID sort is stable, but Geometry sort matches the visual "Waterfall".
        # Let's try Spatial Sort for the Color Spectrum order too!
        complex_nodes.sort(key=lambda nid: (geometries[nid][1], geometries[nid][0]) if nid in geometries else (0,0))
        
        spectral_map: Dict[str, int] = {
            sid: idx for idx, sid in enumerate(complex_nodes)
        }
        total_complex = len(complex_nodes)

        # --- DRAW PASS ---
        for source_id, unsorted_targets in valid_outgoing_map.items():
            # SPATIAL SORTING FOR OUTGOING (Solves the "X-Crossing" at exit point)
            targets = sorted(unsorted_targets, key=get_node_center_x)

            # Retrieve spectral info for this source
            spectral_idx = spectral_map.get(source_id) # None if simple
            
            total_out = len(targets)
            
            for out_idx, target_id in enumerate(targets):
                target_node = nodes_map[target_id]
                
                # Retrieve Incoming Info
                sources_for_target = incoming_map[target_id]
                try:
                    in_idx = sources_for_target.index(source_id)
                except ValueError:
                    in_idx = 0 
                
                total_in = len(sources_for_target)

                # Color Service (Spectral Waterfall)
                color = self.color_service.get_color(
                    spectral_index=spectral_idx,
                    total_complex_nodes=total_complex,
                    edge_index=out_idx,
                    total_edges_from_node=total_out
                )
                
                style = base_edge_style + f"strokeColor={color};"
                
                # Routing Service (Anchors)
                if source_id in geometries and target_id in geometries:
                    anchor = self.routing_service.anchor_style(
                        geometries[source_id],
                        geometries[target_id],
                        out_idx=out_idx, 
                        out_total=total_out,
                        in_idx=in_idx, 
                        in_total=total_in
                    )
                    style += anchor

                self._create_edge(root, xml_ids[source_id], xml_ids[target_id], style)

    # --- HELPERS ---

    def _should_skip_node(self, node: LeafNode, options: VisualizationOptions) -> bool:
        """Centralized filter logic."""
        if node.layer == LayerEnum.COMPOSITION: return True
        if "Error" in node.raw_type or "Exception" in node.raw_type: return True
        if "MARKER" in node.raw_type.upper(): return True
        if options.hide_root_arrows and node.context == "root": return True
        return False

    def _create_edge(self, root, src_id: str, tgt_id: str, style: str) -> None:
        edge_id = str(uuid.uuid4())
        cell = ET.SubElement(root, "mxCell", id=edge_id, style=style, parent="1", source=src_id, target=tgt_id, edge="1")
        ET.SubElement(cell, "mxGeometry", relative="1").set("as", "geometry")

    def _format_node_label(self, label: str, type_str: str) -> str:
        return (
            f'<div style="line-height:1.2;">'
            f'<b style="font-size:15px;">{html.escape(label)}</b><br>'
            f'<span style="font-size:12px;color:#444;">&lt;{html.escape(type_str)}&gt;</span>'
            f"</div>"
        )

    # --- SIDEBAR & GRAPH ELEMENT HELPERS REMAIN UNCHANGED ---
    def _render_sidebar(self, root, towers: List[ContextTower]) -> None:
        context_names = [t.name for t in towers]
        legend_html = get_architecture_legend(context_names)
        self._add_text_block(root, "legend", legend_html, 0, 0, self.README_WIDTH, 24.0)
        
        naming_html = get_naming_cloud_html()
        self._add_text_block(root, "naming", naming_html, 0, 24.5, self.README_WIDTH, 24.0)

    def _add_text_block(self, root, suffix, html_content, x, y, w, h):
        uid = str(uuid.uuid4())
        style = "text;html=1;whiteSpace=wrap;overflow=hidden;rounded=1;strokeColor=#b0bec5;fillColor=#fcfcfc;spacing=10;verticalAlign=top;align=left;"
        cell = ET.SubElement(root, "mxCell", id=uid, value=html_content, style=style, parent="1", vertex="1")
        ET.SubElement(cell, "mxGeometry", x=str(x*self.SCALE), y=str(y*self.SCALE), width=str(w*self.SCALE), height=str(h*self.SCALE)).set("as", "geometry")

    def _add_context_container(self, root, label, x, y, w, h) -> str:
        uid = str(uuid.uuid4())
        style = "swimlane;whiteSpace=wrap;html=1;startSize=30;fillColor=#FFFFFF;strokeColor=#000000;fontStyle=1;fontSize=16;verticalAlign=top;fontColor=#000000;collapsible=1;container=1;recursiveResize=1;"
        cell = ET.SubElement(root, "mxCell", id=uid, value=label, style=style, parent="1", vertex="1")
        ET.SubElement(cell, "mxGeometry", x=str(x*self.SCALE), y=str(y*self.SCALE), width=str(w*self.SCALE), height=str(h*self.SCALE)).set("as", "geometry")
        return uid

    def _add_side_label(self, root, parent_id, label, x, y, w, h):
        uid = str(uuid.uuid4())
        style = "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontColor=#333333;fontStyle=1;fontSize=13;fontFamily=Helvetica;"
        cell = ET.SubElement(root, "mxCell", id=uid, value=label, style=style, parent=parent_id, vertex="1")
        ET.SubElement(cell, "mxGeometry", x=str(x*self.SCALE), y=str(y*self.SCALE), width=str(w*self.SCALE), height=str(h*self.SCALE)).set("as", "geometry")

    def _add_zone_bg(self, root, parent_id, x, y, w, h, color, label):
        uid = str(uuid.uuid4())
        style = (
            f"rounded=1;whiteSpace=wrap;html=1;fillColor={color};strokeColor=none;"
            "pointerEvents=0;arcSize=4;verticalAlign=top;align=center;"
            "fontStyle=1;fontColor=#666666;fontSize=12;spacingTop=4;"
        )
        cell = ET.SubElement(
            root,
            "mxCell",
            id=uid,
            value=label if label else "",
            style=style,
            parent=parent_id,
            vertex="1",
        )
        ET.SubElement(
            cell,
            "mxGeometry",
            x=str(x * self.SCALE),
            y=str(y * self.SCALE),
            width=str(w * self.SCALE),
            height=str(h * self.SCALE),
        ).set("as", "geometry")

    def _add_group_container(self, root, label, x, y, w, h, parent_id) -> str:
        uid = str(uuid.uuid4())
        style = "group;whiteSpace=wrap;html=1;dashed=1;strokeColor=#999999;fillColor=none;verticalAlign=top;align=left;spacing=5;fontStyle=2;fontColor=#666666;fontSize=11;container=1;collapsible=0;"
        cell = ET.SubElement(root, "mxCell", id=uid, value=label, style=style, parent=parent_id, vertex="1")
        ET.SubElement(cell, "mxGeometry", x=str(x*self.SCALE), y=str(y*self.SCALE), width=str(w*self.SCALE), height=str(h*self.SCALE)).set("as", "geometry")
        return uid

    def _add_vertex(self, root, label, x, y, w, h, fill_color, dashed, parent_id="1") -> str:
        uid = str(uuid.uuid4())
        style = f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill_color};strokeColor=#666666;fontColor=#000000;dashed={dashed};shadow=0;fontSize=14;"
        cell = ET.SubElement(root, "mxCell", id=uid, value=label, style=style, parent=parent_id, vertex="1")
        ET.SubElement(cell, "mxGeometry", x=str(x*self.SCALE), y=str(y*self.SCALE), width=str(w*self.SCALE), height=str(h*self.SCALE)).set("as", "geometry")
        return uid