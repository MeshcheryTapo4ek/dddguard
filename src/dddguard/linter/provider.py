from dataclasses import dataclass

import typer
from dishka import Provider, Scope, provide

from .adapters.driving import cli
from .app import CheckProjectUseCase, IScannerGateway
from .domain import RuleEngineService
from .ports.driven.scanner_acl import ScannerAcl
from .ports.driving import LinterFacade


@dataclass(frozen=True, kw_only=True, slots=True)
class LinterContainer:
    """
    Facade Container for Linter Context.
    """

    facade: LinterFacade

    def register_commands(self, app: typer.Typer) -> None:
        """
        Delegates command registration to the driving adapter logic.
        """
        cli.register_commands(app, self.facade)


class LinterProvider(Provider):
    scope = Scope.APP
    # ACL Wiring: Bind Adapter to Interface.
    scanner_gateway = provide(ScannerAcl, provides=IScannerGateway)
    # Domain Service
    rule_engine = provide(RuleEngineService)
    # Application Layer
    check_use_case = provide(CheckProjectUseCase)
    # Driving Port
    facade = provide(LinterFacade)
    # Context Root
    container = provide(LinterContainer)
