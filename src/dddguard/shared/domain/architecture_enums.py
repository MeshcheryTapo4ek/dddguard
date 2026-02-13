from enum import Enum, unique


@unique
class MatchMethod(str, Enum):
    STRUCTURAL = "STRUCT"
    NAME = "NAME"
    UNKNOWN = "UNKNOWN"


@unique
class ScopeEnum(str, Enum):
    ROOT = "ROOT"
    SHARED = "SHARED"
    CONTEXT = "CONTEXT"


@unique
class LayerEnum(str, Enum):
    COMPOSITION = "COMPOSITION"
    DOMAIN = "DOMAIN"
    APP = "APP"
    ADAPTERS = "ADAPTERS"
    PORTS = "PORTS"
    GLOBAL = "GLOBAL"
    UNDEFINED = "UNDEFINED"


@unique
class DirectionEnum(str, Enum):
    DRIVING = "DRIVING"  # Inbound
    DRIVEN = "DRIVEN"  # Outbound
    NONE = "NONE"  # Internal/Agnostic
    ANY = "ANY"  # Universal (e.g. Utils)
    UNDEFINED = "UNDEFINED"


@unique
class DomainType(str, Enum):
    AGGREGATE_ROOT = "AGGREGATE_ROOT"
    ENTITY = "ENTITY"
    VALUE_OBJECT = "VALUE_OBJECT"
    DOMAIN_SERVICE = "DOMAIN_SERVICE"
    DOMAIN_EVENT = "DOMAIN_EVENT"
    FACTORY = "FACTORY"
    SPECIFICATION = "SPECIFICATION"
    POLICY = "POLICY"


@unique
class AppType(str, Enum):
    USE_CASE = "USE_CASE"
    QUERY = "QUERY"
    WORKFLOW = "WORKFLOW"
    INTERFACE = "INTERFACE"
    HANDLER = "HANDLER"


@unique
class PortType(str, Enum):
    # DRIVING (Inbound)
    FACADE = "FACADE"  # Sync Entrypoint
    DISPATCHER = "DISPATCHER"  # Async Event Router

    # DRIVEN (Outbound Interfaces)
    REPOSITORY = "REPOSITORY"
    PUBLISHER = "PUBLISHER"
    GATEWAY = "GATEWAY"
    ACL = "ACL"
    TRANSACTION_MGR = "TRANSACTION_MGR"

    # SHARED / DTOs
    SCHEMA = "SCHEMA"
    MAPPER = "MAPPER"


@unique
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


@unique
class CompositionType(str, Enum):
    CONTAINER = "CONTAINER"
    CONFIG = "CONFIG"
    ENTRYPOINT = "ENTRYPOINT"
    LOGGER = "LOGGER"


@unique
class ArchetypeType(str, Enum):
    ERROR = "ERROR"
    HELPER = "HELPER"
    DECORATOR = "DECORATOR"
    MARKER = "MARKER"
    FOLDER = "FOLDER"
    STUB = "STUB"
    ASSET = "ASSET"
    UNKNOWN = "UNKNOWN"


ComponentType = DomainType | AppType | PortType | AdapterType | CompositionType | ArchetypeType
