from dishka import Provider, Scope, provide

from ..domain import ConfigVo
from ..adapters.driven import YamlConfigLoader


class SharedConfigProvider(Provider):
    """
    DI Provider responsible for bootstrapping the Global Configuration.
    """

    scope = Scope.APP

    @provide
    def provide_loader(self) -> YamlConfigLoader:
        """
        Provides the Driven Adapter capable of reading YAML files.
        """
        return YamlConfigLoader()

    @provide
    def provide_config(self, loader: YamlConfigLoader) -> ConfigVo:
        """
        Uses the Loader to fetch and parse the configuration into a Domain Object.
        """
        return loader.load()
