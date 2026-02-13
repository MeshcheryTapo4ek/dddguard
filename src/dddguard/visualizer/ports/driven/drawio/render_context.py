import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

from ....domain import LeafNode


@dataclass
class RenderContext:
    """
    Mutable state container for the Draw.io rendering process.
    Passes contextual data down the recursive rendering tree, eliminating argument drilling.
    """

    # The XML Root Element where nodes are appended
    root_xml: ET.Element

    # Map: Node ID -> XML ID (mxCell id)
    # Used to link edges between nodes
    xml_ids: dict[str, str] = field(default_factory=dict)

    # Map: Node ID -> Domain Object
    # Used by EdgeTopologyService to analyze node properties
    nodes_map: dict[str, LeafNode] = field(default_factory=dict)

    # Map: Node ID -> (Global X, Global Y, Width, Height)
    # Used by EdgeTopologyService for spatial sorting and routing
    geometries: dict[str, tuple[float, float, float, float]] = field(default_factory=dict)

    def register_node(self, node: LeafNode, xml_id: str, global_x: float, global_y: float) -> None:
        """
        Registers a rendered leaf node into the context.
        """
        if node.id:
            self.xml_ids[node.id] = xml_id
            self.nodes_map[node.id] = node
            self.geometries[node.id] = (global_x, global_y, node.width, node.height)
