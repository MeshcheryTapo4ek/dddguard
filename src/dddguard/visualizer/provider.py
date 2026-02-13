from dataclasses import dataclass

import typer
from dishka import Provider, Scope, provide

from dddguard.shared.domain import ConfigVo

from .adapters.driving import cli as driving_adapter
from .app import (
    CalculateLayoutUseCase,
    DrawArchitectureWorkflow,
    IDiagramRenderer,
    IScannerGateway,
    RenderDiagramUseCase,
)
from .domain import OptimizationConfig, StyleConfig
from .domain import style as default_style
from .ports.driven import DrawioRenderer, ScannerAcl
from .ports.driving.visualizer_facade import VisualizerFacade


@dataclass(frozen=True, kw_only=True, slots=True)
class VisualizerContainer:
    """
    Facade for the Visualizer Context.
    Holds the facade and configuration to expose CLI commands.
    """

    facade: VisualizerFacade
    config: ConfigVo

    def register_commands(self, app: typer.Typer) -> None:
        """
        Delegates command registration to the driving adapter logic.
        """
        driving_adapter.register_commands(app, self.facade, self.config)


class VisualizerProvider(Provider):
    """
    DI Provider for the Visualizer Context.

    Architecture Rule:
    - Provides Ports, Adapters, and App UseCases.
    - NO Domain Services (they are pure static functions called by UseCases).
    """

    scope = Scope.APP

    # --- 0. Configs ---
    @provide(scope=Scope.APP)
    def provide_style(self) -> StyleConfig:
        return default_style

    @provide(scope=Scope.APP)
    def provide_opt_config(self) -> OptimizationConfig:
        return OptimizationConfig()

    # --- 1. Adapters Layer (Driven) ---
    renderer = provide(DrawioRenderer, provides=IDiagramRenderer)
    scanner_gateway = provide(ScannerAcl, provides=IScannerGateway)

    # --- 2. App Layer (Use Cases & Workflow) ---
    # CalculateLayoutUseCase now automatically gets StyleConfig and OptimizationConfig injected
    calculate_layout_uc = provide(CalculateLayoutUseCase)
    render_diagram_uc = provide(RenderDiagramUseCase)
    draw_arch_workflow = provide(DrawArchitectureWorkflow)

    # --- 3. Ports Layer (Driving) ---
    facade = provide(VisualizerFacade)

    # --- 4. Context Root --
    container = provide(VisualizerContainer)
