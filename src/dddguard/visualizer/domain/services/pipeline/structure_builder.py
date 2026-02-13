from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from dddguard.shared.domain import CodeNode

from ...value_objects import StyleConfig, VisualContainer
from ..structure.directory_compressor import DirectoryCompressor
from ..structure.grouping_utils import GroupingUtils
from ..structure.placement_logic import PlacementLogic


@dataclass(frozen=True, kw_only=True, slots=True)
class StructureBuilderService:
    """
    Pipeline Step 2: Structure & Compression.
    Sorts nodes into Architectural Zones (Domain, App, etc.)
    and compresses file paths into a VisualContainer hierarchy.
    """

    @staticmethod
    def build_zone_structure(
        nodes: list[CodeNode], style: StyleConfig
    ) -> dict[str, list[VisualContainer]]:
        # 1. Bucket by Zone (Stateless Placement)
        buckets = defaultdict(list)
        for node in nodes:
            zone = PlacementLogic.resolve_zone(node)
            buckets[zone.value].append(node)

        structure = {}

        # 2. Build & Compress Directories per Zone
        for zone_str, node_list in buckets.items():
            trie_root = StructureBuilderService._build_trie(node_list)

            containers = DirectoryCompressor.compress_and_convert(trie_root, style=style)
            structure[zone_str] = containers

        return structure

    @staticmethod
    def _build_trie(nodes: list[CodeNode]) -> dict[str, Any]:
        """
        Helper to build a raw dictionary trie from nodes.
        """
        root: dict[str, Any] = {"_files": []}
        for node in nodes:
            parts = GroupingUtils.get_semantic_path_parts(node)
            current = root
            for part in parts:
                if part not in current:
                    current[part] = {"_files": []}
                current = current[part]
            current["_files"].append(node)
        return root
