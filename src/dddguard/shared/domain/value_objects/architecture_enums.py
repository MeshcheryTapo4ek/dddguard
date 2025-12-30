from enum import Enum
from typing import Union


class MatchMethod(str, Enum):
    STRUCTURAL = "STRUCT"
    NAME = "NAME"
    UNKNOWN = "UNKNOWN"


class ScopeEnum(str, Enum):
    ROOT = "ROOT"
    SHARED = "SHARED"
    CONTEXT = "CONTEXT"


class LayerEnum(str, Enum):
    COMPOSITION = "COMPOSITION"
    DOMAIN = "DOMAIN"
    APP = "APP"
    ADAPTERS = "ADAPTERS"
    PORTS = "PORTS"
    GLOBAL = "GLOBAL"
    UNDEFINED = "UNDEFINED"


class DirectionEnum(str, Enum):
    DRIVING = "DRIVING"
    DRIVEN = "DRIVEN"
    NONE = "NONE"
    ANY = "ANY"
    UNDEFINED = "UNDEFINED"


LAYER_WEIGHTS = {
    LayerEnum.COMPOSITION: 0,
    LayerEnum.DOMAIN: 1,
    LayerEnum.APP: 2,
    LayerEnum.ADAPTERS: 3,
    LayerEnum.PORTS: 4,
    LayerEnum.GLOBAL: 5,
    LayerEnum.UNDEFINED: 6,
}


class DomainType(str, Enum):
    AGGREGATE_ROOT = "AGGREGATE_ROOT"
    ENTITY = "ENTITY"
    VALUE_OBJECT = "VALUE_OBJECT"
    DOMAIN_SERVICE = "DOMAIN_SERVICE"
    DOMAIN_EVENT = "DOMAIN_EVENT"
    FACTORY = "FACTORY"
    SPECIFICATION = "SPECIFICATION"
    POLICY = "POLICY"


class AppType(str, Enum):
    USE_CASE = "USE_CASE"
    QUERY = "QUERY"
    WORKFLOW = "WORKFLOW"
    INTERFACE = "INTERFACE"
    HANDLER = "HANDLER"


class PortType(str, Enum):
    CONTROLLER = "CONTROLLER"
    CONSUMER = "CONSUMER"
    SCHEDULER = "SCHEDULER"
    CLI = "CLI"
    REPOSITORY = "REPOSITORY"
    PUBLISHER = "PUBLISHER"
    GATEWAY = "GATEWAY"
    ACL = "ACL"
    TRANSACTION_MGR = "TRANSACTION_MGR"
    SCHEMA = "SCHEMA"
    MAPPER = "MAPPER"


class AdapterType(str, Enum):
    CONTROLLER = "CONTROLLER"
    CONSUMER = "CONSUMER"
    SCHEDULER = "SCHEDULER"
    CLI = "CLI"
    REPOSITORY = "REPOSITORY"
    PUBLISHER = "PUBLISHER"
    GATEWAY = "GATEWAY"
    TRANSACTION_MGR = "TRANSACTION_MGR"
    MIDDLEWARE = "MIDDLEWARE"


class CompositionType(str, Enum):
    CONTAINER = "CONTAINER"
    CONFIG = "CONFIG"
    ENTRYPOINT = "ENTRYPOINT"
    LOGGER = "LOGGER"


class ArchetypeType(str, Enum):
    ERROR = "ERROR"
    HELPER = "HELPER"
    DECORATOR = "DECORATOR"
    MARKER = "MARKER"
    STUB = "STUB"
    UNKNOWN = "UNKNOWN"


ComponentType = Union[
    DomainType, AppType, PortType, AdapterType, CompositionType, ArchetypeType
]
