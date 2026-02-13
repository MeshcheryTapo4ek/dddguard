import html
import uuid
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from xml.dom import minidom

from dddguard.shared.assets.asset_legend import get_architecture_legend
from dddguard.shared.assets.naming_cloud import get_naming_cloud_html
from dddguard.shared.helpers.generics import GenericDrivenAdapterError

from ....app import IDiagramRenderer
from ....domain import (
    ContextTower,
    EdgeTopologyService,
    LeafNode,
    StyleConfig,
    VisualContainer,
    VisualElement,
    VisualizationConfig,
)
from ....domain import (
    style as default_style,
)
from .render_context import RenderContext


class FileWriteError(GenericDrivenAdapterError):
    """
    Raised when the renderer fails to write the XML file to disk.
    """

    def __init__(self, path: str, original_error: Exception):
        super().__init__(
            message=f"IO Error writing to {path}: {original_error!s}",
            context_name="Visualizer",
            original_error=original_error,
        )


SCALE: int = 40
README_WIDTH: int = 16
README_PADDING: int = 2


@dataclass(frozen=True, kw_only=True, slots=True)
class DrawioRenderer(IDiagramRenderer):
    """
    Driven adapter: renders context towers as Draw.io XML.
    Uses RenderContext to manage state and EdgeTopologyService for graph logic.
    """

    style_config: StyleConfig = field(init=False, default=default_style)

    def render(
        self,
        towers: list[ContextTower],
        output_path: Path,
        options: VisualizationConfig,
    ) -> None:
        if not towers:
            return

        try:
            # 1. Setup XML Structure
            mxfile = ET.Element("mxfile", host="Electron", agent="DDDGuard", type="device")
            diagram = ET.SubElement(mxfile, "diagram", id=str(uuid.uuid4()), name="Architecture")

            mxGraphModel = ET.SubElement(
                diagram,
                "mxGraphModel",
                dx="0",
                dy="0",
                grid="1",
                gridSize="10",
                guides="1",
                tooltips="1",
                connect="1",
                arrows="1",
                fold="1",
                page="1",
                pageScale="1",
                pageWidth="1169",
                pageHeight="827",
                math="0",
                shadow="0",
            )
            mxGraphModel.set("background", "#FFFFFF")

            root_element = ET.SubElement(mxGraphModel, "root")
            ET.SubElement(root_element, "mxCell", attrib={"id": "0"})
            ET.SubElement(root_element, "mxCell", attrib={"id": "1", "parent": "0"})

            # 2. Render Sidebar (Legend + Naming Cloud)
            self._render_sidebar(root_element, towers)

            # 3. Initialize Context
            ctx = RenderContext(root_xml=root_element)

            x_offset = README_WIDTH + README_PADDING

            # 4. Render Containers & Backgrounds
            for tower in towers:
                tower_x = tower.x + x_offset
                container_id = self._add_context_container(
                    ctx.root_xml,
                    label=f"{tower.name.upper()} CONTEXT",
                    x=tower_x,
                    y=0.0,
                    w=tower.width,
                    h=tower.forced_height,
                )

                for zone in tower.zones:
                    # Side Label (e.g. "DOMAIN")
                    self._add_side_label(
                        ctx.root_xml,
                        parent_id=container_id,
                        label=zone.name,
                        x=0.0,
                        y=zone.backgrounds[0].y_rel if zone.backgrounds else 0.0,
                        w=self.style_config.ZONE_HEADER_WIDTH,
                        h=zone.height,
                    )
                    # Colored Backgrounds
                    for bg in zone.backgrounds:
                        self._add_zone_bg(
                            ctx.root_xml,
                            parent_id=container_id,
                            x=bg.x_rel,
                            y=bg.y_rel,
                            w=bg.width,
                            h=bg.height,
                            color=bg.color,
                            label=bg.label,
                        )

                    # 4.1 Render Nodes Recursively
                    for container in zone.containers:
                        # Absolute coordinates within the Global Canvas
                        abs_x = tower_x + container.x
                        abs_y = container.y

                        self._render_element_recursive(
                            ctx=ctx,
                            element=container,
                            global_x=abs_x,
                            global_y=abs_y,
                            parent_xml_id=container_id,
                            parent_global_x=tower_x,
                            parent_global_y=0.0,
                        )

            # 5. Render Edges (Refactored to use Service)
            self._render_edges(ctx, options)

            # 6. Save File
            xml_str = minidom.parseString(ET.tostring(mxfile)).toprettyxml(indent="  ")
            with output_path.open("w", encoding="utf-8") as f:
                f.write(xml_str)

        except OSError as e:
            raise FileWriteError(str(output_path), e) from e
        except Exception:
            raise

    def _render_element_recursive(
        self,
        ctx: RenderContext,
        element: VisualElement,
        global_x: float,
        global_y: float,
        parent_xml_id: str,
        parent_global_x: float,
        parent_global_y: float,
    ):
        """
        Polymorphic recursive renderer.
        Uses RenderContext to track IDs and Geometries.
        """
        rel_x = global_x - parent_global_x
        rel_y = global_y - parent_global_y

        if isinstance(element, VisualContainer):
            current_xml_id = parent_xml_id

            if element.is_visible:
                current_xml_id = self._add_group_container(
                    ctx.root_xml,
                    element.label,
                    rel_x,
                    rel_y,
                    element.width,
                    element.height,
                    parent_id=parent_xml_id,
                )

            for child in element.children:
                child_global_x = global_x + child.x
                child_global_y = global_y + child.y

                new_parent_gx = global_x if element.is_visible else parent_global_x
                new_parent_gy = global_y if element.is_visible else parent_global_y

                self._render_element_recursive(
                    ctx,
                    child,
                    child_global_x,
                    child_global_y,
                    current_xml_id,
                    parent_global_x=new_parent_gx,
                    parent_global_y=new_parent_gy,
                )

        elif isinstance(element, LeafNode):
            # Safe casing check for interface style
            is_interface = "INTERFACE" in element.raw_type.upper()

            xml_id = self._add_vertex(
                ctx.root_xml,
                label=self._format_node_label(element.label, element.raw_type),
                x=rel_x,
                y=rel_y,
                w=element.width,
                h=element.height,
                fill_color=element.color,
                dashed="1" if is_interface else "0",
                parent_id=parent_xml_id,
            )

            # Register in Context (Refactoring)
            ctx.register_node(element, xml_id, global_x, global_y)

    def _render_edges(
        self,
        ctx: RenderContext,
        options: VisualizationConfig,
    ) -> None:
        """
        Delegates edge calculation to Domain Service.
        The Adapter only draws the result.
        """
        base_edge_style = "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;endArrow=classic;endSize=8;jumpStyle=arc;jumpSize=6;"

        # 1. Call Domain Service to resolve topology
        resolved_edges = EdgeTopologyService.resolve_edges(
            nodes_map=ctx.nodes_map, geometries=ctx.geometries, options=options
        )

        # 2. Draw Result
        for edge in resolved_edges:
            # Safety check: ensure we have XML IDs for both ends
            if edge.source_id not in ctx.xml_ids or edge.target_id not in ctx.xml_ids:
                continue

            style = f"{base_edge_style}strokeColor={edge.color};{edge.anchor_style}"

            self._create_edge(
                ctx.root_xml,
                ctx.xml_ids[edge.source_id],
                ctx.xml_ids[edge.target_id],
                style,
            )

    # --- HELPERS (XML Generation) ---

    def _create_edge(self, root, src_id: str, tgt_id: str, style: str) -> None:
        edge_id = str(uuid.uuid4())
        cell = ET.SubElement(
            root,
            "mxCell",
            attrib={
                "id": edge_id,
                "style": style,
                "parent": "1",
                "source": src_id,
                "target": tgt_id,
                "edge": "1",
            },
        )
        ET.SubElement(cell, "mxGeometry", attrib={"relative": "1", "as": "geometry"})

    def _format_node_label(self, label: str, type_str: str) -> str:
        return (
            f'<div style="line-height:1.2;">'
            f'<b style="font-size:15px;">{html.escape(label)}</b><br>'
            f'<span style="font-size:12px;color:#444;">&lt;{html.escape(type_str)}&gt;</span>'
            f"</div>"
        )

    def _render_sidebar(self, root, towers: list[ContextTower]) -> None:
        context_names = [t.name for t in towers]
        legend_html = get_architecture_legend(context_names)
        self._add_text_block(root, "legend", legend_html, 0, 0, README_WIDTH, 24.0)

        naming_html = get_naming_cloud_html()
        self._add_text_block(root, "naming", naming_html, 0, 24.5, README_WIDTH, 24.0)

    def _add_text_block(self, root, suffix, html_content, x, y, w, h):
        uid = str(uuid.uuid4())
        style = "text;html=1;whiteSpace=wrap;overflow=hidden;rounded=1;strokeColor=#b0bec5;fillColor=#fcfcfc;spacing=10;verticalAlign=top;align=left;"
        cell = ET.SubElement(
            root,
            "mxCell",
            attrib={
                "id": uid,
                "value": html_content,
                "style": style,
                "parent": "1",
                "vertex": "1",
            },
        )
        geom = ET.SubElement(
            cell,
            "mxGeometry",
            attrib={
                "x": str(x * SCALE),
                "y": str(y * SCALE),
                "width": str(w * SCALE),
                "height": str(h * SCALE),
            },
        )
        geom.set("as", "geometry")

    def _add_context_container(self, root, label, x, y, w, h) -> str:
        uid = str(uuid.uuid4())
        style = "swimlane;whiteSpace=wrap;html=1;startSize=30;fillColor=#FFFFFF;strokeColor=#000000;fontStyle=1;fontSize=16;verticalAlign=top;fontColor=#000000;collapsible=1;container=1;recursiveResize=1;"
        cell = ET.SubElement(
            root,
            "mxCell",
            attrib={
                "id": uid,
                "value": label,
                "style": style,
                "parent": "1",
                "vertex": "1",
            },
        )
        geom = ET.SubElement(
            cell,
            "mxGeometry",
            attrib={
                "x": str(x * SCALE),
                "y": str(y * SCALE),
                "width": str(w * SCALE),
                "height": str(h * SCALE),
            },
        )
        geom.set("as", "geometry")
        return uid

    def _add_side_label(self, root, parent_id, label, x, y, w, h):
        uid = str(uuid.uuid4())
        style = "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontColor=#333333;fontStyle=1;fontSize=13;fontFamily=Helvetica;"
        cell = ET.SubElement(
            root,
            "mxCell",
            attrib={
                "id": uid,
                "value": label,
                "style": style,
                "parent": parent_id,
                "vertex": "1",
            },
        )
        geom = ET.SubElement(
            cell,
            "mxGeometry",
            attrib={
                "x": str(x * SCALE),
                "y": str(y * SCALE),
                "width": str(w * SCALE),
                "height": str(h * SCALE),
            },
        )
        geom.set("as", "geometry")

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
            attrib={
                "id": uid,
                "value": label if label else "",
                "style": style,
                "parent": parent_id,
                "vertex": "1",
            },
        )
        geom = ET.SubElement(
            cell,
            "mxGeometry",
            attrib={
                "x": str(x * SCALE),
                "y": str(y * SCALE),
                "width": str(w * SCALE),
                "height": str(h * SCALE),
            },
        )
        geom.set("as", "geometry")

    def _add_group_container(self, root, label, x, y, w, h, parent_id) -> str:
        uid = str(uuid.uuid4())
        style = "group;whiteSpace=wrap;html=1;dashed=1;strokeColor=#999999;fillColor=none;verticalAlign=top;align=left;spacing=5;fontStyle=2;fontColor=#666666;fontSize=11;container=1;collapsible=0;"
        cell = ET.SubElement(
            root,
            "mxCell",
            attrib={
                "id": uid,
                "value": label,
                "style": style,
                "parent": parent_id,
                "vertex": "1",
            },
        )
        geom = ET.SubElement(
            cell,
            "mxGeometry",
            attrib={
                "x": str(x * SCALE),
                "y": str(y * SCALE),
                "width": str(w * SCALE),
                "height": str(h * SCALE),
            },
        )
        geom.set("as", "geometry")
        return uid

    def _add_vertex(self, root, label, x, y, w, h, fill_color, dashed, parent_id="1") -> str:
        uid = str(uuid.uuid4())
        style = f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill_color};strokeColor=#666666;fontColor=#000000;dashed={dashed};shadow=0;fontSize=14;"
        cell = ET.SubElement(
            root,
            "mxCell",
            attrib={
                "id": uid,
                "value": label,
                "style": style,
                "parent": parent_id,
                "vertex": "1",
            },
        )
        geom = ET.SubElement(
            cell,
            "mxGeometry",
            attrib={
                "x": str(x * SCALE),
                "y": str(y * SCALE),
                "width": str(w * SCALE),
                "height": str(h * SCALE),
            },
        )
        geom.set("as", "geometry")
        return uid
