from dataclasses import dataclass
from dishka import make_container, Container, Provider, Scope, provide

from dddguard.scanner import ScannerProvider, ScannerContainer
from dddguard.linter import LinterProvider, LinterContainer
from dddguard.scaffolder import ScaffolderProvider, ScaffolderContainer
from dddguard.visualizer import VisualizerProvider, VisualizerContainer

from dddguard.shared import ConfigVo, YamlConfigLoader


@dataclass(frozen=True, kw_only=True)
class ApplicationContainer:
    """
    Root Container Facade.
    Holds references to context facades for CLI registration.
    """
    scanner: ScannerContainer
    linter: LinterContainer
    scaffolder: ScaffolderContainer
    visualizer: VisualizerContainer


class ConfigProvider(Provider):
    """
    Provides global configuration to the entire application.
    """
    scope = Scope.APP

    @provide
    def provide_config(self) -> ConfigVo:
        loader = YamlConfigLoader()
        return loader.load()


def build_app_container() -> Container:
    """
    Initializes Dishka DI Container with all context providers.
    """
    container = make_container(
        ConfigProvider(),  # <-- Registered here
        ScannerProvider(),
        LinterProvider(),
        ScaffolderProvider(),
        VisualizerProvider(),
    )
    return container