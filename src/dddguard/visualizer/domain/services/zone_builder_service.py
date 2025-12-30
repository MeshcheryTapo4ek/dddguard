from dataclasses import dataclass, field, replace
from typing import Dict, List, Any
from collections import defaultdict

from ..value_objects.visual_primitives import VisualContainer, LeafNode, VisualElement
from ..value_objects.graph import DependencyNode

from .styling.style_service import StyleService
from .placement.node_placement_service import NodePlacementService
from .grouping.node_grouping_service import NodeGroupingService
from .optimization.flow_packing_service import FlowPackingService


@dataclass(frozen=True, kw_only=True, slots=True)
class ZoneBuilderService:
    """
    Domain Service: Orchestrates the creation of the visual structure.
    """

    style: StyleService = field(default_factory=StyleService)
    placement_service: NodePlacementService = field(default_factory=NodePlacementService)
    grouping_service: NodeGroupingService = field(default_factory=NodeGroupingService)
    
    packer: FlowPackingService = field(default_factory=FlowPackingService)

    DEBUG_SHOW_WRAPPERS: bool = True 

    def build_context_structure(
        self, nodes: List[DependencyNode]
    ) -> Dict[str, List[VisualContainer]]:
        """
        Builds a structure: ZoneName -> List[VisualContainer].
        No rows, no sides. Just a flat list of top-level items per zone.
        """

        # 1. Placement Phase (Bucket by Zone only)
        buckets = defaultdict(list)
        for node in nodes:
            zone = self.placement_service.get_placement(node)
            buckets[zone].append(node)

        # 2. Construction Phase
        structure: Dict[str, List[VisualContainer]] = {}

        for zone, bucket_nodes in buckets.items():
            if zone not in structure:
                structure[zone] = []

            containers = self._build_recursive_directory_tree(bucket_nodes)

            structure[zone].extend(containers)

        return structure

    def _build_recursive_directory_tree(
        self,
        nodes: List[DependencyNode],
    ) -> List[VisualContainer]:
        """
        Converts a list of nodes into a nested VisualContainer hierarchy.
        """
        # 1. Build Trie
        root: Dict[str, Any] = {"_files": []}

        for node in nodes:
            parts = self.grouping_service.get_semantic_path_parts(node)
            current_level = root

            for part in parts:
                if part not in current_level:
                    current_level[part] = {"_files": []}
                current_level = current_level[part]

            current_level["_files"].append(self._create_leaf_node(node))

        # 2. Convert Trie to Containers
        return self._convert_trie_to_containers(root)

    def _convert_trie_to_containers(
        self,
        tree_node: Dict[str, Any],
    ) -> List[VisualContainer]:
        """
        Recursively converts the trie.
        """
        results: List[VisualContainer] = []

        # A. Process Sub-folders
        folder_names = [k for k in tree_node.keys() if k != "_files"]

        for folder_name in folder_names:
            sub_tree = tree_node[folder_name]

            # Path Compression
            current_name = folder_name
            current_node = sub_tree

            while True:
                sub_folders = [k for k in current_node.keys() if k != "_files"]
                has_files = len(current_node["_files"]) > 0

                if (not has_files) and (len(sub_folders) == 1):
                    next_folder = sub_folders[0]
                    current_name = f"{current_name}/{next_folder}"
                    current_node = current_node[next_folder]
                else:
                    break

            children = self._convert_trie_to_containers(current_node)

            if children:
                container = self._create_visual_container(
                    label=current_name,
                    children=children,
                    is_visible=True,
                    id_prefix="dir",
                )
                results.append(container)

        # B. Process Files
        for leaf in tree_node["_files"]:
            wrapper = self._wrap_leaf(leaf)
            results.append(wrapper)

        return results

    def _wrap_leaf(self, leaf: LeafNode) -> VisualContainer:
        is_visible = self.DEBUG_SHOW_WRAPPERS
        return self._create_visual_container(
            label=leaf.label, 
            children=[leaf],
            is_visible=is_visible,
            is_leaf_wrapper=True,
            id_prefix="wrap"
        )

    def _create_visual_container(
        self,
        label: str,
        children: List[VisualElement],
        is_visible: bool,
        id_prefix: str,
        is_leaf_wrapper: bool = False,
    ) -> VisualContainer:
        """
        Uses FlowPackingService to determine initial geometry.
        """
        pad_x = self.style.CONTAINER_PAD_X if is_visible else 0.0
        pad_y = self.style.CONTAINER_PAD_Y if is_visible else 0.0

        header_h = 0.8 if is_visible and not is_leaf_wrapper else 0.0
        if is_visible and is_leaf_wrapper:
            header_h = 0.2

        start_x = pad_x
        start_y = header_h + pad_y

        has_only_containers = True
        for ch in children:
            if not isinstance(ch, VisualContainer):
                has_only_containers = False
                break

        gap_x = self.style.CONTAINER_GAP_X if has_only_containers else self.style.LEAF_GAP_X
        gap_y = self.style.CONTAINER_GAP_Y if has_only_containers else self.style.LEAF_GAP_Y

        # Use Packer defaults (aspect ratio driven)
        packed_result = self.packer.pack(
            elements=children,
            start_x=start_x,
            start_y=start_y,
            gap_x=gap_x,
            gap_y=gap_y,
            wrap_width=None 
        )

        positioned_children = packed_result.positioned
        content_right = packed_result.max_right
        content_bottom = packed_result.max_bottom

        total_w = content_right + pad_x if is_visible else content_right
        total_h = content_bottom + pad_y if is_visible else content_bottom

        if is_leaf_wrapper and (not is_visible) and children:
            first = children[0]
            total_w = first.width
            total_h = first.height
            positioned_children = [replace(first, x=0.0, y=0.0)]

        child_id = children[0].id if children else "empty"
        unique_id = f"{id_prefix}_{label}_{child_id}"

        return VisualContainer(
            x=0.0,
            y=0.0,
            width=total_w,
            height=total_h,
            label=label,
            color="none",
            children=positioned_children,
            is_visible=is_visible,
            internal_padding=pad_x,
            id=unique_id,
        )

    def _create_leaf_node(self, node: DependencyNode) -> LeafNode:
        type_str = str(node.component_type).split(".")[-1]
        label = self.style.format_label(node.module_path, type_str)
        imports = [{"module": link.target_module} for link in node.imports]
        
        w = self.style.calculate_node_width(label)
        h = self.style.NODE_HEIGHT
        
        return LeafNode(
            x=0, y=0,
            width=w,
            height=h,
            label=label,
            color=self.style.get_node_color(node.layer, node.scope),
            id=node.module_path,
            layer=node.layer,
            raw_type=type_str,
            context=node.context,
            outgoing_imports=imports
        )