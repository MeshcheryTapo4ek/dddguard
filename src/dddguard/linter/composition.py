from dataclasses import dataclass
import typer
from dishka import Provider, Scope, provide

from dddguard.scanner import ScanProjectUseCase
from dddguard.shared import ConfigVo

from .app import CheckProjectUseCase
from .domain import RuleEngineService
from .adapters.driving.linter_controller import LinterController
from .ports.driving import cli as driving_adapter


@dataclass(frozen=True, kw_only=True, slots=True)
class LinterContainer:
    """Facade for Linter Context."""
    controller: LinterController

    def register_commands(self, app: typer.Typer):
        driving_adapter.register_commands(app, self.controller, self.controller.config)


class LinterProvider(Provider):
    scope = Scope.APP

    @provide
    def provide_rule_engine(self) -> RuleEngineService:
        return RuleEngineService()

    @provide
    def provide_check_use_case(
        self, 
        scanner: ScanProjectUseCase,
        rule_engine: RuleEngineService
    ) -> CheckProjectUseCase:
        return CheckProjectUseCase(
            scan_project=scanner,
            rule_engine=rule_engine
        )

    @provide
    def provide_controller(
        self,
        use_case: CheckProjectUseCase,
        config: ConfigVo
    ) -> LinterController:
        return LinterController(use_case=use_case, config=config)

    @provide
    def provide_container(self, controller: LinterController) -> LinterContainer:
        return LinterContainer(controller=controller)