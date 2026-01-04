from dishka import Provider, Scope, provide

from ..domain import ConfigVo
from ..adapters.driven import YamlConfigLoader


class SharedConfigProvider(Provider):
    scope = Scope.APP

    loader = provide(YamlConfigLoader)

    @provide
    def provide_config(self, loader: YamlConfigLoader) -> ConfigVo:
        return loader.load()