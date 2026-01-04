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
    Holds the controller and configuration to expose CLI commands.
    """
    controller: VisualizerController
    config: ConfigVo

    def register_commands(self, app: typer.Typer) -> None:
        """
        Delegates command registration to the driving adapter logic.
        """
        driving_adapter.register_commands(app, self.controller, self.config)


class VisualizerProvider(Provider):
    """
    DI Provider for the Visualizer Context.
    """
    
    scope = Scope.APP

    # --- 1. Domain Layer (Services & Strategies) ---
    
    # MANUAL PROVIDERS (Primitives Protection):
    # These services depend on primitives (float, int, bool) which breaks auto-wiring.
    
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
    def provide_optimization_config(self) -> OptimizationConfig:
        return OptimizationConfig()

    @provide
    def provide_flow_packing_service(self) -> FlowPackingService:
        # Explicit instantiation allows 'aspect_ratio: float' to take its default value
        return FlowPackingService()

    # AUTO-WIRED SERVICES:
    # These services depend only on other injected classes, so auto-wiring is safe.
    node_placement_service = provide(NodePlacementService)
    node_grouping_service = provide(NodeGroupingService)
    
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
            packer=packer,
        )
    container_optimizer = provide(ContainerOptimizationService)
    
    # Domain Workflows
    optimize_tower_workflow = provide(FindOptimizedTowerWorkflow)

    # --- 2. Adapters Layer (Driven) ---
    @provide
    def provide_renderer(
        self,
        style: StyleService,
        color_service: EdgeColorService,
        routing_service: EdgeRoutingService,
    ) -> IDiagramRenderer:
        return DrawioRenderer(
            style=style,
            color_service=color_service,
            routing_service=routing_service,
        )

    # ACL: Bind ScannerAcl to IScannerGateway
    # Dishka will automatically find ScannerController in the scope.
    scanner_gateway = provide(ScannerAcl, provides=IScannerGateway)

    # --- 3. App Layer (Use Cases & Workflow) ---
    calculate_layout_uc = provide(CalculateLayoutUseCase)
    render_diagram_uc = provide(RenderDiagramUseCase)
    draw_arch_workflow = provide(DrawArchitectureWorkflow)

    # --- 4. Ports Layer (Driving) ---
    controller = provide(VisualizerController)

    # --- 5. Context Root ---
    container = provide(VisualizerContainer)