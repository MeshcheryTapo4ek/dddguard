import uuid
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from dddguard.shared.domain import LayerEnum

from ...value_objects.options import VisualizationConfig
from ...value_objects.visual_primitives import LeafNode
from .edge_color_service import EdgeColorService
from .edge_routing_service import EdgeRoutingService


@dataclass(frozen=True, slots=True, kw_only=True)
class ResolvedEdge:
    source_id: str
    target_id: str
    color: str
    anchor_style: str


@dataclass(frozen=True, slots=True, kw_only=True)
class EdgeTopologyService:
    """
    Domain Service: Orchestrates the calculation of edge paths.

    KEY IMPROVEMENT:
    Implements 'Unified Port Management'. Incoming and Outgoing edges sharing
    the same side of a node are sorted together to prevent collision.
    """

    @staticmethod
    def resolve_edges(
        nodes_map: dict[str, LeafNode],
        geometries: dict[str, tuple[float, float, float, float]],
        options: VisualizationConfig,
    ) -> list[ResolvedEdge]:
        # 1. First Pass: Identify connections & Populate the Unified Port Registry
        # Collect connection points (slots) for each node side
        topology_state = EdgeTopologyService._build_topology_state(nodes_map, geometries, options)

        raw_connections = topology_state["raw_connections"]
        port_registry = topology_state["port_registry"]  # Dict[ "NodeID:SIDE" -> List[SlotInfo] ]
        total_outgoing_counts = topology_state["total_outgoing_counts"]

        # 2. Sort Unified Ports
        # This mixes incoming and outgoing edges on the same face based on the geometry of the *other* node.
        # Result: Arrows flow naturally without crossing at the anchor point.
        EdgeTopologyService._sort_unified_ports(port_registry, geometries)

        # 3. Build Index Map
        # Convert the sorted lists into a fast lookup: ConnectionUUID -> (Index, TotalCount)
        # We need two lookups per connection: one for Source side, one for Target side.
        src_index_map, tgt_index_map = EdgeTopologyService._build_index_maps(port_registry)

        # 4. Prepare Spectral Coloring (Standard Logic)
        complex_nodes = [sid for sid, count in total_outgoing_counts.items() if count >= 1]
        complex_nodes.sort(
            key=lambda nid: (
                geometries[nid][1] if nid in geometries else 0,  # Y
                geometries[nid][0] if nid in geometries else 0,  # X
            )
        )
        spectral_map: dict[str, int] = {sid: idx for idx, sid in enumerate(complex_nodes)}
        total_complex = len(complex_nodes)

        results: list[ResolvedEdge] = []

        # 5. Final Pass: Resolve Each Edge
        for conn in raw_connections:
            uid = conn["uid"]
            src_id = conn["src"]
            tgt_id = conn["tgt"]
            direction = conn["dir"]

            # Retrieve calculated indices from the unified registry
            # Defaults to (0, 1) if something went wrong (shouldn't happen)
            out_idx, out_total = src_index_map.get(uid, (0, 1))
            in_idx, in_total = tgt_index_map.get(uid, (0, 1))

            # A. Calculate Anchor
            # EdgeRoutingService doesn't care if it's mixed in/out.
            # Place anchor at (Index+1)/(Total+1)
            anchor_style = EdgeRoutingService.calculate_anchor(
                direction=direction,
                out_idx=out_idx,
                out_total=out_total,
                in_idx=in_idx,
                in_total=in_total,
            )

            # B. Calculate Color
            # For coloring, we use the specific outgoing index to keep gradients smooth
            # across the bundle leaving the node.
            spectral_idx = spectral_map.get(src_id, 0)

            color = EdgeColorService.get_color(
                spectral_index=spectral_idx,
                total_complex_nodes=total_complex,
                edge_index=out_idx,
                total_edges_from_node=total_outgoing_counts[
                    src_id
                ],  # Use raw count for spread intensity
            )

            results.append(
                ResolvedEdge(
                    source_id=src_id,
                    target_id=tgt_id,
                    color=color,
                    anchor_style=anchor_style,
                )
            )

        return results

    @staticmethod
    def _build_topology_state(
        nodes_map: dict[str, LeafNode],
        geometries: dict[str, tuple[float, float, float, float]],
        options: VisualizationConfig,
    ) -> dict[str, Any]:
        """
        Scans dependencies and registers them into a Unified Port Registry.
        """
        raw_connections = []
        # Registry key: "NodeID:SIDE" (e.g. "auth_service:BOTTOM")
        # Registry value: List of dicts { "conn_uid": ..., "other_node": ... }
        port_registry = defaultdict(list)
        total_outgoing_counts: defaultdict[str, int] = defaultdict(int)

        for source_id, source_node in nodes_map.items():
            if EdgeTopologyService._should_skip_node(source_node, options):
                continue
            if source_id not in geometries:
                continue

            src_geom = geometries[source_id]

            for target_id in source_node.outgoing_imports:
                if target_id not in nodes_map or target_id == source_id:
                    continue
                if target_id not in geometries:
                    continue

                target_node = nodes_map[target_id]

                # Filters
                if EdgeTopologyService._should_skip_node(target_node, options):
                    continue
                if options.hide_shared_arrows and target_node.context == "shared":
                    continue

                # -- Valid Connection Found --
                conn_uid = str(uuid.uuid4())
                tgt_geom = geometries[target_id]
                total_outgoing_counts[source_id] += 1

                # 1. Determine Direction
                direction = EdgeRoutingService.resolve_direction(src_geom, tgt_geom)

                # 2. Determine Physical Sides
                if direction == "DOWN":
                    src_side, tgt_side = "BOTTOM", "TOP"
                elif direction == "UP":
                    src_side, tgt_side = "TOP", "BOTTOM"
                elif direction == "SIDE_RIGHT":
                    src_side, tgt_side = "RIGHT", "LEFT"
                else:  # SIDE_LEFT
                    src_side, tgt_side = "LEFT", "RIGHT"

                src_key = f"{source_id}:{src_side}"
                tgt_key = f"{target_id}:{tgt_side}"

                # 3. Register in Unified Registry
                # For the Source Node, this is an OUTGOING connection to Target
                port_registry[src_key].append(
                    {"conn_uid": conn_uid, "other_node": target_id, "type": "OUT"}
                )

                # For the Target Node, this is an INCOMING connection from Source
                port_registry[tgt_key].append(
                    {"conn_uid": conn_uid, "other_node": source_id, "type": "IN"}
                )

                raw_connections.append(
                    {
                        "uid": conn_uid,
                        "src": source_id,
                        "tgt": target_id,
                        "dir": direction,
                    }
                )

        return {
            "raw_connections": raw_connections,
            "port_registry": port_registry,
            "total_outgoing_counts": total_outgoing_counts,
        }

    @staticmethod
    def _sort_unified_ports(
        port_registry: dict[str, list[dict]],
        geometries: dict[str, tuple[float, float, float, float]],
    ):
        """
        Sorts the slots on every face.
        It looks at the geometry of the 'other_node' to decide ordering.
        """
        for port_key, slots in port_registry.items():
            side = port_key.split(":")[1]

            def get_sort_metric(slot, _side=side):
                nid = slot["other_node"]
                if nid not in geometries:
                    return 0.0
                gx, gy, w, h = geometries[nid]
                center_x = gx + (w / 2.0)
                center_y = gy + (h / 2.0)

                # If the port is on Top/Bottom, we sort arrows by the X position of where they go/come from
                if _side in ["TOP", "BOTTOM"]:
                    return center_x
                # If on Left/Right, sort by Y position
                return center_y

            slots.sort(key=get_sort_metric)

    @staticmethod
    def _build_index_maps(
        port_registry: dict[str, list[dict]],
    ) -> tuple[dict[str, tuple[int, int]], dict[str, tuple[int, int]]]:
        """
        Converts the sorted lists into lookup maps:
        ConnUUID -> (Index, Total)
        """
        src_map = {}
        tgt_map = {}

        for _, slots in port_registry.items():
            total = len(slots)
            for idx, slot in enumerate(slots):
                conn_uid = slot["conn_uid"]
                val = (idx, total)

                # We identify if this slot was registered as source (OUT) or target (IN)
                if slot["type"] == "OUT":
                    src_map[conn_uid] = val
                else:
                    tgt_map[conn_uid] = val

        return src_map, tgt_map

    @staticmethod
    def _should_skip_node(node: LeafNode, options: VisualizationConfig) -> bool:
        if node.layer == LayerEnum.COMPOSITION:
            return True
        raw_upper = node.raw_type.upper()
        if "ERROR" in raw_upper or "EXCEPTION" in raw_upper:
            return True
        if "MARKER" in raw_upper:
            return True
        return bool(options.hide_root_arrows and node.context == "root")
