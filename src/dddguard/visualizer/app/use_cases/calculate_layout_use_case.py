from dataclasses import dataclass, field, replace

from dddguard.shared.domain import CodeGraph

from ...domain import ContextTower, OptimizationConfig, StyleConfig
from ...domain import style as default_style
from ...domain.services.pipeline import (
    GraphGrouperService,
    StructureBuilderService,
    TopologyOptimizerService,
    TowerAssemblerService,
    ZoneLayoutService,
)


@dataclass(frozen=True, kw_only=True, slots=True)
class CalculateLayoutUseCase:
    """
    App Use Case: Orchestrates the calculation of the visual layout.

    Architecture Note:
    - Domain Services are Pure Static Functions.
    - Configuration State is held here and passed down as arguments.
    """

    # 1. Configuration Dependencies (Injected)
    opt_config: OptimizationConfig
    style_config: StyleConfig = field(default=default_style)

    def execute(self, graph: CodeGraph) -> list[ContextTower]:
        """
        Executes the layout calculation pipeline.
        """
        # 1. Grouping: Filter noise and group by Context
        nodes_by_context = GraphGrouperService.group_by_context(graph)

        towers: list[ContextTower] = []
        curr_x = 0.0

        for ctx_name, nodes in sorted(nodes_by_context.items()):
            # 2. Compression: Build directory tree & compress empty folders
            structure = StructureBuilderService.build_zone_structure(nodes, style=self.style_config)

            # 3. Optimization: Reorder for topology (Hill Climbing)
            # Static Call - Passing Configs explicitly
            optimized_structure = TopologyOptimizerService.optimize(
                structure, config=self.opt_config, style_config=self.style_config
            )

            # 4. Packing: Calculate geometry & apply Split Zone logic
            # Static Call - Passing Config explicitly
            zone_layouts = ZoneLayoutService.calculate_zones(
                optimized_structure, style_config=self.style_config
            )

            # 5. Assembly: Finalize Tower aggregate & stretch backgrounds
            # Static Call - Passing Config explicitly
            tower = TowerAssemblerService.assemble(
                ctx_name, zone_layouts, style_config=self.style_config
            )

            # Position tower globally
            tower = replace(tower, x=curr_x)
            towers.append(tower)

            curr_x += tower.width + self.style_config.TOWER_PAD_X

        return towers
