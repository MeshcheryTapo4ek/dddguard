from enum import Enum
from typing import TypeAlias, Union


class ProjectBoundedContextNames(str, Enum):
    """
    Top-level categorization of the code location.
    """
    COMPOSITION_ROOT = "root"
    SHARED = "shared"
    CONTEXT = "context"


class ContextLayerEnum(str, Enum):
    """
    Defines horizontal architectural layers (DDD/Hexagonal).
    """
    DOMAIN = "domain"
    APP = "app"

    # Interface Adapters
    DRIVING_ADAPTERS = "driving_adapters"  # Inputs (Controllers, Consumers)
    DRIVEN_ADAPTERS = "driven_adapters"    # Outputs (Gateways, Repositories)

    # Data Transfer Objects
    DRIVING_DTO = "driving_dto"
    DRIVEN_DTO = "driven_dto"

    # Infrastructure Ports (Low-level implementation)
    DRIVING_PORTS = "driving_ports"
    DRIVEN_PORTS = "driven_ports"

    COMPOSITION = "composition"
    OTHER = "other"


# --- Component Types (Level 3 Granularity) ---

class DomainTypeEnum(str, Enum):
    """Core domain components."""
    ENTITY = "Entity"
    VALUE_OBJECT = "ValueObject"
    AGGREGATE_ROOT = "AggregateRoot"
    DOMAIN_SERVICE = "DomainService"
    DOMAIN_EVENT = "DomainEvent"
    DOMAIN_ERROR = "DomainError"
    FACTORY = "Factory"


class AppTypeEnum(str, Enum):
    """Application orchestration components."""
    USE_CASE = "UseCase"
    QUERY = "Query"
    WORKFLOW = "Workflow"
    HANDLER = "Handler"
    INTERFACE = "Interface"
    APP_ERROR = "AppError"

class DrivenAdapterEnum(str, Enum):
    """Secondary adapters (Outbound/Driven)."""
    REPOSITORY = "Repository"
    TRANSACTION_MANAGER = "TransactionManager"
    GATEWAY = "Gateway"
    ACL_FACADE = "AclFacade"
    PUBLISHER = "Publisher"
    ADAPTER_ERROR = "AdapterError"


class DrivingAdapterEnum(str, Enum):
    """Primary adapters (Inbound/Driving)."""
    CONTROLLER = "Controller"
    CONSUMER = "Consumer"
    ADAPTER_ERROR = "AdapterError"


class PortTypeEnum(str, Enum):
    """Infrastructure implementations."""
    INFRASTRUCTURE_IMPL = "InfrastructureImplementation"


class DtoTypeEnum(str, Enum):
    """Data structures for layer boundaries."""
    REQUEST_DTO = "RequestDTO"
    RESPONSE_DTO = "ResponseDTO"


class CompositionTypeEnum(str, Enum):
    """Wiring and assembly components."""
    CONTAINER = "Container"
    WIRING = "Wiring"


class OtherTypeEnum(str, Enum):
    OTHER = "Other"


# Explicit Type Alias for readability
AnyComponentType: TypeAlias = Union[
    DomainTypeEnum,
    AppTypeEnum,
    DrivenAdapterEnum,
    DrivingAdapterEnum,
    PortTypeEnum,
    DtoTypeEnum,
    CompositionTypeEnum,
    OtherTypeEnum,
]