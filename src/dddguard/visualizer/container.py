from dataclasses import dataclass
import typer
from dishka import Provider, Scope, provide

from dddguard.scanner import ScanProjectUseCase
from dddguard.shared import ConfigVo
from .app import (
    DrawArchitectureWorkflow,
    CalculateLayoutUseCase,
    RenderDiagramUseCase,
    IDiagramRenderer,
)
from .adapters.driven import DrawioRenderer
from .adapters.driving import VisualizerController
from .ports.driving import cli as driving_adapter

from .domain import (
    StyleService, EdgeColorService, EdgeRoutingService, ZoneBuilderService,
    HorizontalAligner, VerticalStacker
)

@dataclass(frozen=True, kw_only=True, slots=True)
class VisualizerContainer:
    """
    Facade for the Visualizer Context.
    Holds Controller (Adapter) for the Presentation Layer.
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
    def provide_zone_builder_service(self, style: StyleService) -> ZoneBuilderService:
        return ZoneBuilderService(style=style)

    # --- Domain Layout Strategies ---
    @provide
    def provide_horizontal_aligner(self, style: StyleService) -> HorizontalAligner:
        return HorizontalAligner(style=style)

    @provide
    def provide_vertical_stacker(self, style: StyleService) -> VerticalStacker:
        return VerticalStacker(style=style)


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

    # 3. App Layer (Use Cases & Workflow)

    @provide
    def provide_calculate_layout_use_case(
        self,
        style: StyleService,
        builder: ZoneBuilderService,
        aligner: HorizontalAligner,
        stacker: VerticalStacker,
    ) -> CalculateLayoutUseCase:
        return CalculateLayoutUseCase(
            style=style,
            builder=builder,
            aligner=aligner,
            stacker=stacker,
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
        scanner: ScanProjectUseCase,
        calculate_layout: CalculateLayoutUseCase,
        render_diagram: RenderDiagramUseCase,
    ) -> DrawArchitectureWorkflow:
        return DrawArchitectureWorkflow(
            scan_project=scanner,
            calculate_layout=calculate_layout,
            render_diagram=render_diagram,
        )

    # 4. Adapters Layer (Driving)
    @provide
    def provide_visualizer_controller(
        self,
        workflow: DrawArchitectureWorkflow,
        config: ConfigVo
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