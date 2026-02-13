from ...value_objects.options import OptimizationConfig, StyleConfig
from ...value_objects.visual_primitives import VisualContainer, VisualElement
from ..geometry.container_optimizer import ContainerOptimizationService


class TopologyOptimizerService:
    """
    Pipeline Step 3: Optimization.
    Reorders containers (Hill Climbing) to minimize arrow crossing.
    PURE STATIC IMPLEMENTATION.
    """

    @staticmethod
    def optimize(
        structure: dict[str, list[VisualElement]],
        config: OptimizationConfig,
        style_config: StyleConfig,
    ) -> dict[str, list[VisualElement]]:
        """
        Applies topological and heuristic sorting to the lists of containers within zones.
        Absorbed logic from the deprecated TowerOptimizer.
        """
        optimized_structure = {}

        # Define which zones benefit from optimization (ordering based on dependencies)
        target_zones = [
            "DOMAIN",
            "APP",
            "PORTS_DRIVING",
            "PORTS_DRIVEN",
            "ADAPTERS_DRIVING",
            "ADAPTERS_DRIVEN",
            "COMPOSITION",
        ]

        for zone_name, items in structure.items():
            # 1. Optimize the internal tree of each container (recursive)
            deep_optimized = []
            for item in items:
                if isinstance(item, VisualContainer):
                    # Recurse down into folders/containers
                    optimized_item = ContainerOptimizationService.optimize_container_tree(
                        container=item, config=config, style_config=style_config
                    )
                    deep_optimized.append(optimized_item)
                else:
                    # It's a LeafNode (File), nothing inside to optimize
                    deep_optimized.append(item)

            # 2. Optimize the order of the siblings in the list
            # Note: optimize_sibling_list handles both Containers and Leaves (polymorphic via VisualElement)
            # providing they implement walk_leaves() and have geometry.
            if zone_name in target_zones and len(deep_optimized) > 1:
                # We cast to List[VisualContainer] technically, but the service handles VisualElements
                # as long as they behave like elements with ID and dimensions.
                # Ideally ContainerOptimizationService signatures should be updated to VisualElement,
                # but Python runtime allows this duck typing if methods match.
                final_list = ContainerOptimizationService.optimize_sibling_list(
                    siblings=deep_optimized, config=config, style_config=style_config
                )
            else:
                final_list = deep_optimized

            optimized_structure[zone_name] = final_list

        return optimized_structure
