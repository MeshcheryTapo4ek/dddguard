from dataclasses import dataclass
import typer
from dishka import Provider, Scope, provide

from dddguard.scanner import ScannerController

from dddguard.shared import ConfigVo
from ..app import (
    DrawArchitectureWorkflow,
    CalculateLayoutUseCase,
    RenderDiagramUseCase,
    IDiagramRenderer,
    IScannerGateway,
    FindOptimizedTowerWorkflow,
)
from ..ports.driven import DrawioRenderer, ScannerAcl

from ..ports.driving import VisualizerController
from ..adapters.driving import cli as driving_adapter

from ..domain import (
    StyleService,
    EdgeColorService,
    EdgeRoutingService,
    ZoneBuilderService,
    NodePlacementService,
    NodeGroupingService,
    OptimizationConfig,
    ContainerOptimizationService,
    FlowPackingService,
)


@dataclass(frozen=True, kw_only=True, slots=True)
class VisualizerContainer:
    """
    Facade for the Visualizer Context.
    """
    controller: VisualizerController
    config: ConfigVo

    def register_commands(self, app: typer.Typer) -> None:
        driving_adapter.register_commands(app, self.controller, self.config)


class VisualizerProvider(Provider):
    scope = Scope.APP

    # 1. Domain Layer (Services & Strategies)
    @provide
    def provide_style_service(self) -> StyleService:
        return StyleService()

    @provide
    def provide_edge_color_service(self) -> EdgeColorService:
        return EdgeColorService()

    @provide
    def provide_edge_routing_service(self) -> EdgeRoutingService:
        return EdgeRoutingService()

    @provide
    def provide_node_placement_service(self) -> NodePlacementService:
        return NodePlacementService()

    @provide
    def provide_node_grouping_service(self) -> NodeGroupingService:
        return NodeGroupingService()
    
    @provide
    def provide_flow_packing_service(self) -> FlowPackingService:
        return FlowPackingService()

    @provide
    def provide_zone_builder_service(
        self,
        style: StyleService,
        placement: NodePlacementService,
        grouping: NodeGroupingService,
        packer: FlowPackingService,
    ) -> ZoneBuilderService:
        return ZoneBuilderService(
            style=style,
            placement_service=placement,
            grouping_service=grouping,
            packer=packer
        )

    @provide
    def provide_optimization_config(self) -> OptimizationConfig:
        return OptimizationConfig()

    @provide
    def provide_container_optimization_service(
        self,
        style: StyleService,
        cfg: OptimizationConfig,
        packer: FlowPackingService,
    ) -> ContainerOptimizationService:
        return ContainerOptimizationService(style=style, config=cfg, packer=packer)

    @provide
    def provide_find_optimized_tower_workflow(
        self,
        optimizer: ContainerOptimizationService,
    ) -> FindOptimizedTowerWorkflow:
        return FindOptimizedTowerWorkflow(optimizer=optimizer)


    # 2. Adapters Layer (Driven)
    @provide
    def provide_renderer(
        self,
        style: StyleService,
        edge_colors: EdgeColorService,
        edge_routing: EdgeRoutingService,
    ) -> IDiagramRenderer:
        return DrawioRenderer(
            style=style,
            color_service=edge_colors,
            routing_service=edge_routing,
        )

    # ACL
    @provide
    def provide_scanner_gateway(self, controller: ScannerController) -> IScannerGateway:
        return ScannerAcl(controller=controller)

    # 3. App Layer (Use Cases & Workflow)
    @provide
    def provide_calculate_layout_use_case(
        self,
        style: StyleService,
        builder: ZoneBuilderService,
        optimize_tower: FindOptimizedTowerWorkflow,
        packer: FlowPackingService,
    ) -> CalculateLayoutUseCase:
        return CalculateLayoutUseCase(
            style=style,
            builder=builder,
            optimize_tower=optimize_tower,
            packer=packer,
        )

    @provide
    def provide_render_diagram_use_case(
        self,
        renderer: IDiagramRenderer,
    ) -> RenderDiagramUseCase:
        return RenderDiagramUseCase(renderer=renderer)

    @provide
    def provide_draw_architecture_workflow(
        self,
        gateway: IScannerGateway,
        calculate_layout: CalculateLayoutUseCase,
        render_diagram: RenderDiagramUseCase,
    ) -> DrawArchitectureWorkflow:
        return DrawArchitectureWorkflow(
            scanner_gateway=gateway,
            calculate_layout=calculate_layout,
            render_diagram=render_diagram,
        )

    # 4. Ports Layer (Driving)
    @provide
    def provide_visualizer_controller(
        self, workflow: DrawArchitectureWorkflow, config: ConfigVo
    ) -> VisualizerController:
        return VisualizerController(workflow=workflow, config=config)

    # 5. Context Root
    @provide
    def provide_container(
        self,
        controller: VisualizerController,
        config: ConfigVo,
    ) -> VisualizerContainer:
        return VisualizerContainer(
            controller=controller,
            config=config,
        )