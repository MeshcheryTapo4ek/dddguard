from typing import List, Dict, Tuple

from ..domain.enums import (
    ProjectBoundedContextNames,
    ContextLayerEnum,
    DomainTypeEnum,
    AppTypeEnum,
    DrivenAdapterEnum,
    DrivingAdapterEnum,
    PortTypeEnum,
    DtoTypeEnum,
    CompositionTypeEnum,
    AnyComponentType
)
from ..domain.rules import ClassificationRule

CTX = ProjectBoundedContextNames.CONTEXT


# 1. Regex Rules for Scanner (Strict identification)

RULES_REGISTRY: List[ClassificationRule] = [
    # --- DOMAIN ---
    ClassificationRule(CTX, ContextLayerEnum.DOMAIN, DomainTypeEnum.ENTITY, [r".*entity$", r".*_ent$", r".*model$"]),
    ClassificationRule(CTX, ContextLayerEnum.DOMAIN, DomainTypeEnum.VALUE_OBJECT, [r".*vo$", r".*valueobject$", r".*value$", r".*value_object$"]),
    ClassificationRule(CTX, ContextLayerEnum.DOMAIN, DomainTypeEnum.AGGREGATE_ROOT, [r".*aggregate$", r".*root$"]),
    ClassificationRule(CTX, ContextLayerEnum.DOMAIN, DomainTypeEnum.DOMAIN_SERVICE, [r".*service$", r".*policy$", r".*rule$", r".*logic$"]),
    ClassificationRule(CTX, ContextLayerEnum.DOMAIN, DomainTypeEnum.DOMAIN_EVENT, [r".*event$", r".*occurred$"]),
    ClassificationRule(CTX, ContextLayerEnum.DOMAIN, DomainTypeEnum.FACTORY, [r".*factory$"]),
    ClassificationRule(CTX, ContextLayerEnum.DOMAIN, DomainTypeEnum.DOMAIN_ERROR, [r".*error$", r".*exception$", r".*failure$"], path_pattern=r".*/domain/.*"),

    # --- APP ---
    ClassificationRule(CTX, ContextLayerEnum.APP, AppTypeEnum.USE_CASE, [r".*use_?case$", r".*command$", r".*action$", r".*interactor$"]),
    ClassificationRule(CTX, ContextLayerEnum.APP, AppTypeEnum.QUERY, [r".*query$", r".*finder$", r".*reader$"]),
    ClassificationRule(CTX, ContextLayerEnum.APP, AppTypeEnum.WORKFLOW, [r".*workflow$", r".*saga$", r".*process$"]),
    ClassificationRule(CTX, ContextLayerEnum.APP, AppTypeEnum.INTERFACE, [r"^i[A-Z].*", r".*interface$", r".*port$", r".*protocol$"]),
    ClassificationRule(CTX, ContextLayerEnum.APP, AppTypeEnum.APP_ERROR, [r".*error$", r".*exception$", r".*failure$"], path_pattern=r".*/app/.*"),

    # --- DRIVEN ADAPTERS ---
    ClassificationRule(CTX, ContextLayerEnum.DRIVEN_ADAPTERS, DrivenAdapterEnum.REPOSITORY, [r".*repo(sitory)?$"], path_pattern=r".*/adapters/driven/.*"),
    ClassificationRule(CTX, ContextLayerEnum.DRIVEN_ADAPTERS, DrivenAdapterEnum.GATEWAY, [r".*gateway$", r".*client$", r".*connector$", r".*adapter$"], path_pattern=r".*/adapters/driven/.*"),
    ClassificationRule(CTX, ContextLayerEnum.DRIVEN_ADAPTERS, DrivenAdapterEnum.TRANSACTION_MANAGER, [r".*uow$", r".*unitofwork$", r".*manager$", r".*committer$"], path_pattern=r".*/adapters/driven/.*"),
    ClassificationRule(CTX, ContextLayerEnum.DRIVEN_ADAPTERS, DrivenAdapterEnum.ACL_FACADE, [r".*facade$", r".*acl$"], path_pattern=r".*/adapters/driven/.*"),
    ClassificationRule(CTX, ContextLayerEnum.DRIVEN_ADAPTERS, DrivenAdapterEnum.PUBLISHER, [r".*publisher$", r".*producer$", r".*broadcaster$", r".*sender$"], path_pattern=r".*/adapters/driven/.*"),
    ClassificationRule(CTX, ContextLayerEnum.DRIVEN_ADAPTERS, DrivenAdapterEnum.ADAPTER_ERROR, [r".*error$", r".*exception$"], path_pattern=r".*/adapters/driven/.*"),

    # --- DRIVING ADAPTERS ---
    ClassificationRule(CTX, ContextLayerEnum.DRIVING_ADAPTERS, DrivingAdapterEnum.CONTROLLER, [r".*controller$", r".*view$", r".*router$", r".*endpoint$", r".*api$"], path_pattern=r".*/adapters/driving/.*"),
    ClassificationRule(CTX, ContextLayerEnum.DRIVING_ADAPTERS, DrivingAdapterEnum.CONSUMER, [r".*consumer$", r".*subscriber$", r".*listener$", r".*handler$"], path_pattern=r".*/adapters/driving/.*"),
    ClassificationRule(CTX, ContextLayerEnum.DRIVING_ADAPTERS, DrivingAdapterEnum.ADAPTER_ERROR, [r".*error$", r".*exception$"], path_pattern=r".*/adapters/driving/.*"),

    # --- DTOs ---
    ClassificationRule(CTX, ContextLayerEnum.DRIVING_DTO, DtoTypeEnum.REQUEST_DTO, [r".*request$", r".*input$", r".*payload$", r".*in$"], path_pattern=r".*/dtos?/driving/.*"),
    ClassificationRule(CTX, ContextLayerEnum.DRIVEN_DTO, DtoTypeEnum.RESPONSE_DTO, [r".*response$", r".*output$", r".*viewmodel$", r".*out$"], path_pattern=r".*/dtos?/driven/.*"),

    # --- PORTS ---
    ClassificationRule(CTX, ContextLayerEnum.DRIVEN_PORTS, PortTypeEnum.INFRASTRUCTURE_IMPL, [r".*db$", r".*engine$", r".*session$", r".*client$"], path_pattern=r".*/ports/driven/.*"),
    ClassificationRule(CTX, ContextLayerEnum.DRIVING_PORTS, PortTypeEnum.INFRASTRUCTURE_IMPL, [r".*server$", r".*cli$", r".*app$"], path_pattern=r".*/ports/driving/.*"),

    # --- COMPOSITION ---
    ClassificationRule(CTX, ContextLayerEnum.COMPOSITION, CompositionTypeEnum.WIRING, [r".*container$", r".*wiring$", r"main", r"bootstrap"]),
]

# 2. Token Keywords for Heuristics (Soft identification for Visualizer/Cloud)

NAMING_CONVENTIONS: Dict[Tuple[ContextLayerEnum, AnyComponentType], List[str]] = {

    # 1. DOMAIN LAYER

    (ContextLayerEnum.DOMAIN, DomainTypeEnum.ENTITY): [
        "entities", "entity", "ent", "models", "model"
    ],
    (ContextLayerEnum.DOMAIN, DomainTypeEnum.VALUE_OBJECT): [
        "value_objects", "value_object", "values", "value", "vo", "vos",
        "types", "type", "enums", "enum",
        "domain_primitives", "primitives", "primitive"
    ],
    (ContextLayerEnum.DOMAIN, DomainTypeEnum.AGGREGATE_ROOT): [
        "aggregates", "aggregate", "agg"
    ],
    (ContextLayerEnum.DOMAIN, DomainTypeEnum.DOMAIN_SERVICE): [
        "services", "service", "policies", "policy", "logic", "rules"
    ],
    (ContextLayerEnum.DOMAIN, DomainTypeEnum.DOMAIN_EVENT): [
        "events", "event", "domain_events"
    ],
    (ContextLayerEnum.DOMAIN, DomainTypeEnum.FACTORY): [
        "factories", "factory"
    ],
    (ContextLayerEnum.DOMAIN, DomainTypeEnum.DOMAIN_ERROR): [
        "domain_errors", "errors", "exceptions"
    ],


    # 2. APP LAYER

    (ContextLayerEnum.APP, AppTypeEnum.USE_CASE): [
        "use_cases", "use_case", "usecases", "usecase", "ucs", "uc",
        "commands", "command", "interactors", "interactor", "actions", "action"
    ],
    (ContextLayerEnum.APP, AppTypeEnum.QUERY): [
        "queries", "query", "readers", "finders"
    ],
    (ContextLayerEnum.APP, AppTypeEnum.WORKFLOW): [
        "workflows", "workflow", "sagas", "saga", "process"
    ],
    (ContextLayerEnum.APP, AppTypeEnum.HANDLER): [
        "handlers", "handler"
    ],
    (ContextLayerEnum.APP, AppTypeEnum.INTERFACE): [
        "interfaces", "interface", "protocols", "ports"
    ],
    (ContextLayerEnum.APP, AppTypeEnum.APP_ERROR): [
        "app_errors"
    ],


    # 3. ADAPTERS (DRIVEN / OUTBOUND)

    (ContextLayerEnum.DRIVEN_ADAPTERS, DrivenAdapterEnum.REPOSITORY): [
        "repositories", "repository", "repos", "repo",
        "providers", "provider", "readers", "reader"
    ],
    (ContextLayerEnum.DRIVEN_ADAPTERS, DrivenAdapterEnum.GATEWAY): [
        "gateways", "gateway", "clients", "client", "integrations", "integration"
    ],
    (ContextLayerEnum.DRIVEN_ADAPTERS, DrivenAdapterEnum.TRANSACTION_MANAGER): [
        "persistence", "transactions", "transaction", "uow", "unit_of_work", "manager"
    ],
    (ContextLayerEnum.DRIVEN_ADAPTERS, DrivenAdapterEnum.ACL_FACADE): [
        "facades", "facade", "acl"
    ],
    (ContextLayerEnum.DRIVEN_ADAPTERS, DrivenAdapterEnum.PUBLISHER): [
        "publishers", "publisher", "pub", "producers", "producer", "prod", "broadcasters"
    ],


    # 4. ADAPTERS (DRIVING / INBOUND)

    (ContextLayerEnum.DRIVING_ADAPTERS, DrivingAdapterEnum.CONTROLLER): [
        "controllers", "controller", "controll", "control",
        "views", "view", "endpoints", "routers", "router", "api"
    ],
    (ContextLayerEnum.DRIVING_ADAPTERS, DrivingAdapterEnum.CONSUMER): [
        "consumers", "consumer", "listeners", "listener",
        "subscribers", "subscriber", "sub"
    ],


    # 5. DTOs

    (ContextLayerEnum.DRIVING_DTO, DtoTypeEnum.REQUEST_DTO): [
        "requests", "request", "req", "inputs", "input", "delivering", "payloads"
    ],
    (ContextLayerEnum.DRIVEN_DTO, DtoTypeEnum.RESPONSE_DTO): [
        "responses", "response", "res", "outputs", "output", "delivers", "viewmodels"
    ],


    # 6. PORTS

    (ContextLayerEnum.DRIVING_PORTS, PortTypeEnum.INFRASTRUCTURE_IMPL): [
        "cli", "console", "http", "rest", "graphql", "server"
    ],
    (ContextLayerEnum.DRIVEN_PORTS, PortTypeEnum.INFRASTRUCTURE_IMPL): [
        "db", "database", "sql", "supabase", "postgres", "mongo", "redis",
        "http_clients", "message_bus", "smtp", "s3"
    ],


    # 7. COMPOSITION

    (ContextLayerEnum.COMPOSITION, CompositionTypeEnum.WIRING): [
        "composition", "wiring", "containers", "container", "bootstrap", "main"
    ],
}


def get_flat_token_map() -> Dict[str, Tuple[ContextLayerEnum, AnyComponentType]]:
    """Helper to convert structured conventions into a flat search map."""
    flat_map = {}
    for (layer, comp_type), tokens in NAMING_CONVENTIONS.items():
        for token in tokens:
            flat_map[token] = (layer, comp_type)
    return flat_map