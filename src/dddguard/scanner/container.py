from dataclasses import dataclass
import typer
from dishka import Provider, Scope, provide

from .app import ScanProjectUseCase, ClassifyFileUseCase, IProjectReader
from .domain import (
    AstImportParserService,
    ScopeHeuristicService,
    LayerHeuristicService,
    RegexMatcherService,
)
from .adapters.driven import FSProjectReader
from .adapters.driving.scanner_controller import ScannerController
from .ports.driving import cli as driving_adapter
from dddguard.shared import ConfigVo


@dataclass(frozen=True, kw_only=True, slots=True)
class ScannerContainer:
    """
    Facade for the Scanner Context.
    Exposes Controller (Driving Adapter) to the Presentation Layer (CLI).
    """
    controller: ScannerController

    def register_commands(self, app: typer.Typer):
        driving_adapter.register_commands(app, self.controller)


class ScannerProvider(Provider):
    scope = Scope.APP

    # --- Adapters (Driven) ---
    @provide
    def provide_reader(self, config: ConfigVo) -> IProjectReader:
        return FSProjectReader(config=config)

    # --- Domain Services ---
    @provide
    def provide_parser_service(self) -> AstImportParserService:
        return AstImportParserService()

    @provide
    def provide_scope_service(self) -> ScopeHeuristicService:
        return ScopeHeuristicService()

    @provide
    def provide_layer_service(self) -> LayerHeuristicService:
        return LayerHeuristicService()

    @provide
    def provide_regex_service(self) -> RegexMatcherService:
        return RegexMatcherService()

    # --- App Use Cases ---
    
    @provide
    def provide_classify_use_case(
        self,
        scope: ScopeHeuristicService,
        layer: LayerHeuristicService,
        regex: RegexMatcherService,
    ) -> ClassifyFileUseCase:
        return ClassifyFileUseCase(
            scope_service=scope,
            layer_service=layer,
            regex_service=regex,
        )

    @provide
    def provide_scan_use_case(
        self,
        reader: IProjectReader,
        classifier: ClassifyFileUseCase,
        parser: AstImportParserService,
    ) -> ScanProjectUseCase:
        return ScanProjectUseCase(
            project_reader=reader, 
            classifier=classifier, 
            parser=parser
        )

    # --- Adapters (Driving) ---
    @provide
    def provide_controller(
        self, 
        use_case: ScanProjectUseCase, 
        config: ConfigVo
    ) -> ScannerController:
        return ScannerController(use_case=use_case, config=config)

    # --- Context Facade ---
    @provide
    def provide_container(
        self, 
        controller: ScannerController
    ) -> ScannerContainer:
        return ScannerContainer(controller=controller)