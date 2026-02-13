from dishka import Provider, Scope, provide

from .adapters.driven.yaml_config_loader import YamlConfigLoader
from .domain import ConfigVo


class SharedProvider(Provider):
    scope = Scope.APP

    loader = provide(YamlConfigLoader)

    @provide
    def provide_config(self, loader: YamlConfigLoader) -> ConfigVo:
        return loader.load()
