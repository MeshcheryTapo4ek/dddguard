from dataclasses import dataclass
import typer
from dishka import Provider, Scope, provide

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
    """
    Facade for Linter Context.
    """
    controller: LinterController

    def register_commands(self, app: typer.Typer) -> None:
        """
        Delegates command registration to the driving adapter logic.
        """
        driving_adapter.register_commands(app, self.controller)


class LinterProvider(Provider):
    """
    DI Provider for the Linter Context.
    Wires the Rule Engine and the ACL to the Scanner Context.
    """
    
    scope = Scope.APP

    # Domain Layer
    rule_engine = provide(RuleEngineService)

    # ACL Wiring: Bind Adapter to Interface.
    # Dishka automatically injects the external ScannerController into ScannerAcl.
    scanner_gateway = provide(ScannerAcl, provides=IScannerGateway)

    # Application Layer
    check_use_case = provide(CheckProjectUseCase)

    # Driving Port
    controller = provide(LinterController)

    # Context Root
    container = provide(LinterContainer)