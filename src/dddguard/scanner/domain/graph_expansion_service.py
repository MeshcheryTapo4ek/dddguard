from collections import deque
from dataclasses import dataclass

from dddguard.shared.domain import CodeGraph


@dataclass(frozen=True, slots=True, kw_only=True)
class GraphExpansionService:
    """
    Domain Service: Graph Expansion (Additive Logic).

    Responsible for revealing hidden dependencies in the CodeGraph.
    It takes a set of "Visible" nodes and traverses their imports (outgoing edges)
    up to a specified `depth`.

    Algorithm:
    Uses Breadth-First Search (BFS) with 'budget tracking' to ensure we capture
    dependencies reachable within N hops, resolving circular dependencies gracefully.
    """

    @staticmethod
    def expand(
        graph: CodeGraph,
        initial_visible: set[str],
        depth: int,
    ) -> set[str]:
        """
        Executes the expansion logic.

        :param graph: The fully linked CodeGraph (containing all nodes).
        :param initial_visible: The set of Node IDs (paths) currently visible (seeds).
        :param depth: Recursion depth.
                      0 = Strict (no expansion).
                      1 = Include direct imports.
                      2 = Include imports of imports.
        :return: A superset of initial_visible containing discovered dependencies.
        """
        # Optimization: Zero depth means no work needed
        if depth <= 0:
            return initial_visible

        # We start with what is already visible
        final_visible = set(initial_visible)

        # BFS Queue structure: (NodeID, RemainingDepthBudget)
        queue: deque[tuple[str, int]] = deque((node_id, depth) for node_id in initial_visible)

        # Visited Map: NodeID -> MaxBudgetSeen
        # Critical for BFS efficiency: We only re-process a node if we reach it
        # with a HIGHER budget than before (meaning we found a shorter path to it,
        # allowing us to go deeper into its children).
        visited: dict[str, int] = dict.fromkeys(initial_visible, depth)

        while queue:
            current_id, budget = queue.popleft()

            # If no budget left to explore neighbors, stop this branch
            if budget <= 0:
                continue

            # Resolve Node
            # Assuming graph.nodes is Dict[str, Node]
            current_node = graph.nodes.get(current_id)
            if not current_node:
                continue

            # Traverse Outgoing Edges (Imports)
            for target_id in current_node.imports:
                new_budget = budget - 1

                # Additive Logic:
                # 1. New Node? Add to visible & queue.
                # 2. Existing Node but found via shorter path (more budget)? Update & requeue.
                if target_id not in visited or visited[target_id] < new_budget:
                    visited[target_id] = new_budget
                    final_visible.add(target_id)
                    queue.append((target_id, new_budget))

        return final_visible
