from collections import defaultdict
from collections.abc import Sequence

from ...value_objects.visual_primitives import VisualElement

# Type Alias for Weight Matrix Key
PairKey = tuple[str, str]


class DependencyWeigher:
    """
    Stateless Domain Service helper.
    Calculates the connectivity weights between a set of visual elements
    based on the imports of their internal LeafNodes.
    """

    @staticmethod
    def calculate_weights(
        elements: Sequence[VisualElement],
    ) -> tuple[dict[PairKey, float], dict[str, set[str]]]:
        """
        Builds a weight matrix and adjacency list for the provided elements.

        Algorithm:
        1. Map every internal LeafNode to its owner (one of the `elements`).
        2. Iterate through all leaves to find imports that cross between owners.
        3. Accumulate weights (bidirectional) and adjacency (directional).
        """
        if not elements:
            return {}, {}

        # 1. Map Leaf ID -> Owner ID
        leaf_to_owner: dict[str, str] = {}
        for owner in elements:
            if not owner.id:
                continue
            for leaf in owner.walk_leaves():
                if leaf.id:
                    leaf_to_owner[leaf.id] = owner.id

        if not leaf_to_owner:
            return {}, {}

        weights: dict[PairKey, float] = {}
        adjacency: dict[str, set[str]] = defaultdict(set)

        # 2. Iterate owners to find connections
        for owner in elements:
            if not owner.id:
                continue

            # We treat the owner as the source of the connection
            src_owner_id = owner.id
            if src_owner_id not in adjacency:
                adjacency[src_owner_id] = set()

            for leaf in owner.walk_leaves():
                if not leaf.id:
                    continue

                # Check outgoing imports from this leaf
                for tgt_leaf_id in leaf.outgoing_imports:
                    tgt_owner_id = leaf_to_owner.get(tgt_leaf_id)

                    # Ignore internal links (within the same owner) or links to outside scope
                    if tgt_owner_id is None or tgt_owner_id == src_owner_id:
                        continue

                    # Record Directed Adjacency
                    adjacency[src_owner_id].add(tgt_owner_id)

                    # Record Symmetric Weight
                    # Normalize key order to ensure A->B and B->A contribute to the same weight entry
                    a, b = (
                        (src_owner_id, tgt_owner_id)
                        if src_owner_id < tgt_owner_id
                        else (tgt_owner_id, src_owner_id)
                    )
                    key: PairKey = (a, b)
                    weights[key] = weights.get(key, 0.0) + 1.0

        return weights, dict(adjacency)
