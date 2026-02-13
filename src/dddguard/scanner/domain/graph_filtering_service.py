from dataclasses import dataclass
from pathlib import Path

from dddguard.shared.domain import ArchetypeType, CodeGraph, CodeNode


@dataclass(frozen=True, slots=True, kw_only=True)
class GraphFilteringService:
    """
    Domain Service: Graph Filtering (Subtractive Logic).

    Responsible for applying the "Narrowing Phase" of the scan.
    It determines which nodes in the classified graph are 'Visible' based on
    a combination of Physical Location (Focus) and Architectural Constraints (Whitelists).
    """

    @staticmethod
    def determine_initial_focus(
        graph: CodeGraph,
        focus_path: Path,
        whitelist_layers: list[str] | None,
        whitelist_contexts: list[str] | None,
        include_assets: bool = True,
    ) -> set[str]:
        """
        Filters the graph nodes to produce a set of 'Surviving Nodes'.

        **Filtering Strategy:**
        A node survives if:
        1.  **Candidate Check:** It is physically inside the `focus_path` OR it belongs
            to an explicitly whitelisted Context (including Root/Shared).
        2.  **Logical Check:** It satisfies all architectural whitelists (Context, Layer)
            and type constraints (Assets).

        :param graph: The CLASSIFIED CodeGraph.
        :param focus_path: The physical directory we are focusing on.
        :param whitelist_layers: List of allowed layers (e.g., ['DOMAIN']). None = All.
        :param whitelist_contexts: List of allowed contexts (including 'root', 'shared'). None = All.
        :param include_assets: Whether to include non-code files.
        :return: A set of Node Paths (IDs) that are visible.
        """
        surviving_nodes: set[str] = set()

        # Pre-process arguments for O(1) lookups
        focus_path_str = str(focus_path.resolve())
        allowed_layers = set(whitelist_layers) if whitelist_layers else None
        allowed_contexts = set(whitelist_contexts) if whitelist_contexts else None

        for path, node in graph.nodes.items():
            # 0. Safety: Skip unclassified nodes (cannot apply logic to them)
            if not node.passport:
                continue

            # 1. Candidate Check (Physical Location & Explicit Inclusion)
            is_candidate = GraphFilteringService._is_physical_candidate(
                node, focus_path_str, allowed_contexts
            )
            if not is_candidate:
                continue

            # 2. Logical Check (Architectural Constraints)
            if not GraphFilteringService._is_logically_allowed(
                node, allowed_layers, allowed_contexts, include_assets
            ):
                continue

            # If all gates passed, the node survives
            surviving_nodes.add(path)

        return surviving_nodes

    @staticmethod
    def prune_graph(
        graph: CodeGraph,
        visible_modules: set[str],
    ) -> set[str]:
        """
        Finalizes the graph state based on the visibility set.

        Mutates the graph nodes:
        - Nodes in `visible_modules` -> marked as `FINALIZED` (Visible).
        - Other nodes -> remain `CLASSIFIED` (Hidden/Background).

        :return: The set of finalized node paths.
        """
        final_set = set()

        for path, node in graph.nodes.items():
            if path in visible_modules:
                node.finalize()
                final_set.add(path)
            # Implicit else: Node remains hidden.

        return final_set

    # --- INTERNAL HELPERS ---

    @staticmethod
    def _is_physical_candidate(
        node: CodeNode,
        focus_path_str: str,
        allowed_contexts: set[str] | None,
    ) -> bool:
        """
        Determines if a node is a candidate for visibility.

        Strategy:
        - If `allowed_contexts` is set: Does the node belong to one of them? (Overrides physical path).
        - Else (No context filter): Is the node inside the physical `focus_path`?
        """
        # A. Explicit Context Inclusion (e.g. User selected 'shared' or 'root')
        if allowed_contexts and node.passport and node.passport.context_name in allowed_contexts:
            return True

        # B. Physical Check (Default behavior)
        # We assume node.file_path is absolute (set during Detection).
        if node.file_path:
            node_path_str = str(node.file_path.resolve())
            if node_path_str.startswith(focus_path_str):
                return True

        return False

    @staticmethod
    def _is_logically_allowed(
        node: CodeNode,
        allowed_layers: set[str] | None,
        allowed_contexts: set[str] | None,
        include_assets: bool,
    ) -> bool:
        """
        Determines if a candidate satisfies all architectural constraints.
        """
        passport = node.passport
        if passport is None:
            return False

        # 1. Asset Filter
        if not include_assets and passport.component_type == ArchetypeType.ASSET:
            return False

        # 2. Layer Filter
        if allowed_layers and passport.layer.value not in allowed_layers:
            return False

        # 3. Context Filter
        # If whitelist exists, the node MUST match one of the allowed contexts.
        if allowed_contexts is not None:
            if not passport.context_name or passport.context_name not in allowed_contexts:
                return False

        return True
