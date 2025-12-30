from dataclasses import dataclass
import typer

from dishka import Provider, Scope, provide

# App & Domain Imports
from ..app import (
    ScanProjectUseCase,
    ClassifyTreeUseCase,
    ClassifyFileUseCase,
    IProjectReader,
)
from ..domain import (
    AstImportParserService,
    SrmEngineService,
    ModuleResolutionService,
    DependencyExpansionService, 
)


from ..ports.driven import FileSystemRepository
from ..ports.driving import ScannerController

from ..adapters.driving import register_commands

from dddguard.shared import ConfigVo


@dataclass(frozen=True, kw_only=True, slots=True)
class ScannerContainer:
    """
    Composition Root Facade for the Scanner Bounded Context.
    """

    controller: ScannerController

    def register_commands(self, app: typer.Typer) -> None:
        """Wires context driving ports to the global CLI."""
        register_commands(app, self.controller)


class ScannerProvider(Provider):
    """
    Dependency Injection provider for the Scanner context.
    """

    scope = Scope.APP

    # --- Driven Adapters (Repositories) ---
    @provide
    def provide_reader(self, config: ConfigVo) -> IProjectReader:
        # Strict Naming: The implementation is a Repository
        return FileSystemRepository(config=config)

    # --- Domain Services ---
    @provide
    def provide_parser_service(self) -> AstImportParserService:
        return AstImportParserService()

    @provide
    def provide_srm_engine(self) -> SrmEngineService:
        return SrmEngineService()

    @provide
    def provide_module_resolver(self) -> ModuleResolutionService:
        return ModuleResolutionService()

    @provide
    def provide_dependency_service(self) -> DependencyExpansionService:
        # NEW: Register the expansion service
        return DependencyExpansionService()

    # --- Use Cases ---
    @provide
    def provide_classify_use_case(
        self, srm_engine: SrmEngineService
    ) -> ClassifyFileUseCase:
        return ClassifyFileUseCase(srm_engine=srm_engine)

    @provide
    def provide_scan_use_case(
        self,
        reader: IProjectReader,
        classifier: ClassifyFileUseCase,
        parser: AstImportParserService,
        module_resolver: ModuleResolutionService,
        dependency_service: DependencyExpansionService, # <--- Injected
    ) -> ScanProjectUseCase:
        return ScanProjectUseCase(
            project_reader=reader,
            classifier=classifier,
            parser=parser,
            module_resolver=module_resolver,
            dependency_service=dependency_service,
        )

    @provide
    def provide_classify_tree_use_case(
        self, srm_engine: SrmEngineService
    ) -> ClassifyTreeUseCase:
        return ClassifyTreeUseCase(srm_engine=srm_engine)

    # --- Driving Port (Controller) ---
    @provide
    def provide_controller(
        self,
        scan_use_case: ScanProjectUseCase,
        classify_tree_use_case: ClassifyTreeUseCase,
        config: ConfigVo,
    ) -> ScannerController:
        return ScannerController(
            scan_use_case=scan_use_case,
            classify_use_case=classify_tree_use_case,
            config=config,
        )

    # --- Container Facade ---
    @provide
    def provide_container(self, controller: ScannerController) -> ScannerContainer:
        return ScannerContainer(controller=controller)