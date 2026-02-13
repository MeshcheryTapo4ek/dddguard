from collections import defaultdict
from dataclasses import dataclass

from dddguard.shared.domain import ArchetypeType, CodeGraph, CodeNode


@dataclass(frozen=True, slots=True)
class GraphGrouperService:
    """
    Pipeline Step 1: Scanning & Grouping.
    Filters noise from the raw graph and groups nodes by Bounded Context.
    """

    @staticmethod
    def group_by_context(graph: CodeGraph) -> dict[str, list[CodeNode]]:
        nodes_by_context = defaultdict(list)

        for node in graph.nodes.values():
            if not node.passport:
                continue

            # Policy: Skip markers
            if node.passport.component_type == ArchetypeType.MARKER:
                continue

            # Policy: Skip external or unknown contexts
            ctx_name = node.passport.context_name
            if not ctx_name or ctx_name == "external":
                continue

            nodes_by_context[ctx_name].append(node)

        return nodes_by_context
