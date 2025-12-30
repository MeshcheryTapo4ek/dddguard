from dataclasses import dataclass
import typer
from dishka import Provider, Scope, provide

# External Context
from dddguard.scanner import ScannerController
from dddguard.shared import ConfigVo

# Internal App Layer
from ..app import CheckProjectUseCase, IScannerGateway

# Internal Domain Layer
from ..domain import RuleEngineService

# Internal Adapters (Driving)
from ..adapters.driving import cli as driving_adapter
from ..ports.driving import LinterController

# Internal Adapters (Driven / ACL)
from ..ports.driven import ScannerAcl


@dataclass(frozen=True, kw_only=True, slots=True)
class LinterContainer:
    """Facade for Linter Context."""

    controller: LinterController

    def register_commands(self, app: typer.Typer):
        driving_adapter.register_commands(app, self.controller)


class LinterProvider(Provider):
    scope = Scope.APP

    @provide
    def provide_rule_engine(self) -> RuleEngineService:
        return RuleEngineService()

    # --- ACL WIRING START ---
    @provide
    def provide_scanner_gateway(self, controller: ScannerController) -> IScannerGateway:
        """
        Wraps the external ScannerController in our local ACL Adapter.
        Returns it as the Interface required by the App Layer.
        """
        return ScannerAcl(controller=controller)

    # --- ACL WIRING END ---

    @provide
    def provide_check_use_case(
        self, gateway: IScannerGateway, rule_engine: RuleEngineService
    ) -> CheckProjectUseCase:
        """
        Injects the Interface (Gateway), not the concrete Controller.
        """
        return CheckProjectUseCase(scanner_gateway=gateway, rule_engine=rule_engine)

    @provide
    def provide_controller(
        self, use_case: CheckProjectUseCase, config: ConfigVo
    ) -> LinterController:
        return LinterController(use_case=use_case, config=config)

    @provide
    def provide_container(self, controller: LinterController) -> LinterContainer:
        return LinterContainer(controller=controller)
