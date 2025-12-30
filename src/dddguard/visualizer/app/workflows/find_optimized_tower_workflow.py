from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from ...domain import VisualContainer
from ...domain.services.optimization import ContainerOptimizationService

# Simplified structure: ZoneName -> List[VisualContainer]
StructureT = Dict[str, List[VisualContainer]]


@dataclass(frozen=True, kw_only=True, slots=True)
class FindOptimizedTowerWorkflow:
    """
    App Workflow: optimizes container ordering.
    Operates on a flat list of containers per zone (No Rows).
    """

    optimizer: ContainerOptimizationService

    def execute(self, structure: StructureT) -> StructureT:
        optimized: StructureT = {}

        for zone_name, containers in structure.items():
            # 1) Optimize internal structure of each container (Recursive)
            internal_optimized = [
                self.optimizer.optimize_container_tree(c) for c in containers
            ]

            # 2) Optimize order of the top-level items in this Zone.
            # We treat the Zone list as one big sibling group.
            # The optimizer will use weights + external anchors to sort them.
            sibling_optimized = self.optimizer.optimize_sibling_list(internal_optimized)

            optimized[zone_name] = sibling_optimized

        return optimized