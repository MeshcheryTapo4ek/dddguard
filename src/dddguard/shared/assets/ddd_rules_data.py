from ..domain.architecture_enums import (
    AdapterType,
    AppType,
    ArchetypeType,
    ComponentType,
    CompositionType,
    DirectionEnum,
    DomainType,
    LayerEnum,
    PortType,
    ScopeEnum,
)

# Type aliases for the nested registry structures
ScopeRegistry = dict[ScopeEnum, list[str]]
LayerRegistry = dict[LayerEnum, list[str]]
DirectionRegistry = dict[DirectionEnum, list[str]]
StructuralRegistry = dict[LayerEnum, dict[DirectionEnum, dict[ComponentType, list[str]]]]
NamingRegistry = dict[LayerEnum, dict[DirectionEnum, dict[ComponentType, list[str]]]]


# Mapping Scope to folder tokens
_SCOPE_REGISTRY: ScopeRegistry = {
    ScopeEnum.ROOT: [r"^root$"],
    ScopeEnum.SHARED: [r"^shared$", r"^common$", r"^global$", r"^utils?$"],
}

# Mapping Layer to folder tokens
_LAYER_REGISTRY: LayerRegistry = {
    LayerEnum.DOMAIN: [r"^domain$"],
    LayerEnum.APP: [r"^app$", r"^application$"],
    LayerEnum.PORTS: [r"^ports?$"],
    LayerEnum.ADAPTERS: [r"^adapters?$", r"^infrastructure$", "^external$", r"^infra$"],
    LayerEnum.COMPOSITION: [
        r"^composition$",
        r"^wiring$",
        r"^bootstrap$",
        r"^entrypoints?$",
        r"^configs?$",
    ],
    LayerEnum.GLOBAL: [
        r"^helpers?$",
        r"^utils?$",
        r"^common$",
        r"^tools?$",
        r"^support$",
        r"^lib$",
        r"^core$",
    ],
}

# Mapping Direction to folder tokens
_DIRECTION_REGISTRY: DirectionRegistry = {
    DirectionEnum.DRIVING: [r"^driving$", r"^inbound$", r"^input$", r"^in$"],
    DirectionEnum.DRIVEN: [r"^driven$", r"^outbound$", r"^output$", r"^out$"],
}

_STRUCTURAL_REGISTRY: StructuralRegistry = {
    LayerEnum.DOMAIN: {
        DirectionEnum.NONE: {
            DomainType.AGGREGATE_ROOT: [r"^aggregates?$", r"^aggs?$", r"^roots?$"],
            DomainType.ENTITY: [r"^entities?$", r"^ents?$"],
            DomainType.VALUE_OBJECT: [
                r"^value_?objects?$",
                r"^vos?$",
                r"^values?$",
                r"^enums?$",
                r"^constants?$",
                r"^types?$",
            ],
            DomainType.DOMAIN_SERVICE: [
                r"^services?$",
                r"^svcs?$",
                r"^logic$",
                r"^calculators?$",
                r"^processors?$",
            ],
            DomainType.DOMAIN_EVENT: [
                r"^events?$",
                r"^domain_events?$",
                r"^messages?$",
                r"^signals?$",
            ],
            DomainType.FACTORY: [r"^factories?$", r"^builders?$", r"^assemblers?$"],
            DomainType.SPECIFICATION: [
                r"^specifications?$",
                r"^specs?$",
                r"^criteria$",
                r"^predicates?$",
                r"^registries?$",
            ],
            DomainType.POLICY: [r"^policies?$", r"^strategies?$", r"^rules?$"],
        }
    },
    LayerEnum.APP: {
        DirectionEnum.NONE: {
            AppType.USE_CASE: [
                r"^use_?cases?$",
                r"^ucs?$",
                r"^interactors?$",
                r"^actions?$",
                r"^operations?$",
            ],
            AppType.QUERY: [r"^queries?$", r"^reads?$", r"^finders?$", r"^searchers?$"],
            AppType.WORKFLOW: [
                r"^workflows?$",
                r"^sagas?$",
                r"^processes?$",
                r"^pipelines?$",
            ],
            AppType.INTERFACE: [
                r"^interfaces?$",
                r"^ports?$",
                r"^boundaries?$",
                r"^spi$",
            ],
            AppType.HANDLER: [
                r"^handlers?$",
                r"^listeners?$",
                r"^receivers?$",
                r"^subscribers?$",
            ],
        }
    },
    LayerEnum.PORTS: {
        DirectionEnum.DRIVING: {
            PortType.FACADE: [
                r".*facade$",
            ],
            PortType.DISPATCHER: [
                r".*dispatcher$",
            ],
        },
        DirectionEnum.DRIVEN: {
            PortType.REPOSITORY: [
                r"^repositories?$",
                r"^repos?$",
                r"^db$",
                r"^storage$",
                r"^sql$",
                r"^mongo$",
                r"^postgres$",
                r".*dao$",
            ],
            PortType.PUBLISHER: [
                r"^publishers?$",
                r"^producers?$",
                r"^senders?$",
                r"^emitters?$",
                r"^message_bus$",
                r"^broker$",
                r"^bus$",
            ],
            PortType.GATEWAY: [
                r".*gateways?$",
                r"^clients?$",
                r"^integrations?$",
                r"^providers?$",
                r"^external$",
                r"^remote$",
            ],
            PortType.ACL: [r"^acl$", r"^anti_corruption_layer$"],
            PortType.TRANSACTION_MGR: [r"^uow$", r"^unit_of_work$", r"^transactions?$"],
        },
        DirectionEnum.ANY: {
            PortType.SCHEMA: [
                r"^schemas?$",
                r"^models?$",
                r"^requests?$",
                r"^responses?$",
                r"^types?$",
                r"^json$",
                r"^dtos?$",
            ],
            PortType.MAPPER: [
                r"^mappers?$",
                r"^converters?$",
                r"^serializers?$",
                r"^transformers?$",
            ],
        },
    },
    LayerEnum.ADAPTERS: {
        DirectionEnum.DRIVING: {
            AdapterType.CONTROLLER: [
                r"^controllers?$",
                r"^api$",
                r"^routers?$",
                r"^endpoints?$",
                r"^views?$",
                r"^handlers?$",
                r"^rest$",
                r"^graphql$",
            ],
            AdapterType.CONSUMER: [
                r"^consumers?$",
                r"^workers?$",
                r"^subscribers?$",
                r"^listeners?$",
                r"^jobs?$",
                r"^tasks?$",
                r"^queues?$",
            ],
            AdapterType.SCHEDULER: [
                r"^schedulers?$",
                r"^cron$",
                r"^periodic$",
                r"^beats?$",
            ],
            AdapterType.CLI: [
                r".*tui$",
                r".*wizard$",
                r".*cli$",
                r".*command$",
                r".*menu$",
                r".*console$",
            ],
        },
        DirectionEnum.DRIVEN: {
            AdapterType.REPOSITORY: [
                r"^db$",
                r"^database$",
                r"^sql$",
                r"^mongo$",
                r"^postgres$",
                r"^redis$",
                r"^migrations?$",
                r"^alembic$",
                r"^storage$",
                r"^s3$",
                r"^dynamo.*",
                r"^dao$",
            ],
            AdapterType.PUBLISHER: [
                r"^broker$",
                r"^kafka$",
                r"^rabbit$",
                r"^nats$",
                r"^messaging$",
                r"^streams?$",
                r"^producers?$",
                r"^bus$",
            ],
            AdapterType.GATEWAY: [
                r"^gateways?$",
                r"^clients?$",
                r"^integrations?$",
                r"^providers?$",
                r"^external$",
                r"^remote$",
                r"^http$",
                r"^grpc$",
                r"^soap$",
                r"^aws$",
            ],
            AdapterType.TRANSACTION_MGR: [
                r"^uow$",
                r"^unit_of_work$",
                r"^transactions?$",
            ],
        },
        DirectionEnum.ANY: {
            AdapterType.MIDDLEWARE: [
                r"^middleware$",
                r"^middlewares?$",
                r"^cors$",
                r"^interceptors?$",
            ],
        },
    },
    LayerEnum.COMPOSITION: {
        DirectionEnum.NONE: {
            CompositionType.CONTAINER: [
                r"^composition$",
                r"^di$",
                r"^ioc$",
                r"^providers?$",
                r"^wiring$",
                r"^bootstrap$",
                r"^modules?$",
                r"^injection$",
                r"^containers?$",
            ],
            CompositionType.CONFIG: [
                r"^config$",
                r"^configs?$",
                r"^settings?$",
                r"^env$",
                r"^options$",
            ],
            CompositionType.ENTRYPOINT: [
                r"^entrypoints?$",
                r"^apps?$",
                r"^server$",
                r"^web$",
                r"^api$",
                r"^cli$",
                r"^main$",
                r"^manage$",
                r"^asgi$",
                r"^wsgi$",
            ],
            CompositionType.LOGGER: [r"^logging$", r"^loggers?$", r"^logs?$"],
        }
    },
    LayerEnum.GLOBAL: {
        DirectionEnum.ANY: {
            ArchetypeType.ERROR: [r"^exceptions?$", r"^errors?$", r"^failures?$"],
            ArchetypeType.HELPER: [
                r"^utils?$",
                r"^helpers?$",
                r"^tools?$",
                r"^common$",
                r"^support$",
            ],
            ArchetypeType.DECORATOR: [r"^decorators?$", r"^wrappers?$"],
            ArchetypeType.STUB: [r"^stubs?$", r"^mocks?$", r"^fakes?$", r"^tests?$"],
            ArchetypeType.ASSET: [r"^assets?$", r"^resources?$", r"^templates?$"],
        }
    },
}

_NAMING_REGISTRY: NamingRegistry = {
    LayerEnum.DOMAIN: {
        DirectionEnum.NONE: {
            DomainType.AGGREGATE_ROOT: [r".*aggregate$", r".*root$", r".*agg$"],
            DomainType.ENTITY: [r".*entity$", r".*ent$"],
            DomainType.VALUE_OBJECT: [
                r".*vo$",
                r".*value$",
                r".*kind$",
                r".*type$",
                r".*types$",
                r".*info$",
                r".*status$",
                r".*const$",
                r".*enums?$",
                r".*assets?$",
                r".*resources?$",
                r".*templates?$",
            ],
            DomainType.DOMAIN_SERVICE: [
                r".*service$",
                r".*svc$",
                r".*calculator$",
                r".*processor$",
                r".*logic$",
            ],
            DomainType.DOMAIN_EVENT: [
                r".*event$",
                r".*occurred$",
                r".*msg$",
                r".*signal$",
            ],
            DomainType.FACTORY: [r".*factory$", r".*builder$", r".*assembler$"],
            DomainType.SPECIFICATION: [
                r".*spec$",
                r".*specification$",
                r".*predicate$",
                r".*criteria$",
                r".*registry$",
            ],
            DomainType.POLICY: [r".*policy$", r".*strategy$", r".*rule$"],
        }
    },
    LayerEnum.APP: {
        DirectionEnum.NONE: {
            AppType.USE_CASE: [
                r".*use_case$",
                r".*service$",
                r".*interactor$",
                r".*action$",
                r".*executor$",
                r"^uc_.*",
                r".*_uc$",
            ],
            AppType.QUERY: [
                r".*query$",
                r".*lookup$",
                r".*selector$",
                r".*resolver$",
                r"^q_.*",
            ],
            AppType.WORKFLOW: [
                r".*workflows?$",
                r".*saga$",
                r".*orchestrator$",
                r".*coordinator$",
                r".*process$",
            ],
            AppType.INTERFACE: [
                r"^i_.*",
                r".*interface$",
                r".*contract$",
                r".*abc$",
            ],
            AppType.HANDLER: [
                r".*handler$",
                r".*listener$",
                r".*subscriber$",
                r"^on_.*",
            ],
        }
    },
    LayerEnum.PORTS: {
        DirectionEnum.DRIVING: {
            PortType.FACADE: [
                r".*facade$",
            ],
            PortType.DISPATCHER: [
                r".*dispatcher$",
            ],
        },
        DirectionEnum.DRIVEN: {
            PortType.REPOSITORY: [r".*repository$", r".*repo$", r".*dao$"],
            PortType.PUBLISHER: [
                r".*publisher$",
                r".*producer$",
                r".*sender$",
                r".*bus$",
            ],
            PortType.GATEWAY: [
                r".*gateways?$",
                r".*client$",
                r".*connector$",
                r".*renderer$",
                r".*service$",
                r".*painter$",
            ],
            PortType.ACL: [r".*acl$"],
            PortType.TRANSACTION_MGR: [r".*uow$", r".*manager$", r".*transaction$"],
        },
        DirectionEnum.ANY: {
            PortType.SCHEMA: [
                r".*schema$",
                r".*req$",
                r".*res$",
                r".*dto$",
                r".*model$",
                r".*msg$",
                r"^req_.*",
                r"^res_.*",
            ],
            PortType.MAPPER: [
                r".*mapper$",
                r".*converter$",
                r".*serializer$",
                r".*transformer$",
            ],
        },
    },
    LayerEnum.ADAPTERS: {
        DirectionEnum.DRIVING: {
            AdapterType.CONTROLLER: [
                r".*controller$",
                r".*router$",
                r".*handler$",
                r".*viewset$",
                r".*api$",
            ],
            AdapterType.CONSUMER: [
                r".*consumer$",
                r".*worker$",
                r".*processor$",
                r".*listener$",
            ],
            AdapterType.SCHEDULER: [r".*scheduler$", r".*cron$", r".*job$"],
            AdapterType.CLI: [
                r".*cli$",
                r".*command$",
                r".*wizard$",
                r".*viewer$",
                r".*tui$",
            ],
        },
        DirectionEnum.DRIVEN: {
            AdapterType.REPOSITORY: [
                r".*repository$",
                r".*repo$",
                r".*dao$",
                r".*db$",
                r".*adapter$",
            ],
            AdapterType.PUBLISHER: [
                r".*publisher$",
                r".*producer$",
                r".*sender$",
                r".*bus$",
            ],
            AdapterType.GATEWAY: [
                r".*gateways?$",
                r".*client$",
                r".*connector$",
                r".*service$",
                r".*provider$",
                r".*renderers?$",
            ],
            AdapterType.TRANSACTION_MGR: [r".*uow$", r".*manager$", r".*transaction$"],
        },
        DirectionEnum.ANY: {
            AdapterType.MIDDLEWARE: [r".*middleware$", r".*interceptor$"],
        },
    },
    LayerEnum.COMPOSITION: {
        DirectionEnum.NONE: {
            CompositionType.CONTAINER: [
                r".*container$",
                r".*module$",
                r".*provider$",
                r".*registry$",
                r".*wiring$",
                r".*di$",
                r"^factory$",
            ],
            CompositionType.CONFIG: [
                r".*config$",
                r".*settings$",
                r".*env$",
                r".*options$",
                r"^config$",
                r"^settings$",
            ],
            CompositionType.ENTRYPOINT: [
                r"^run$",
                r"^application$",
                r"^main$",
                r"^app$",
                r"^manage$",
                r"^asgi$",
                r"^wsgi$",
                r"^cli$",
            ],
            CompositionType.LOGGER: [r".*logger$", r".*logging$"],
        }
    },
    LayerEnum.GLOBAL: {
        DirectionEnum.ANY: {
            ArchetypeType.ERROR: [r".*error$", r".*exception$", r".*failure$"],
            ArchetypeType.HELPER: [
                r".*utils?$",
                r".*helpers?$",
                r".*tools?$",
                r".*funcs?$",
                r".*common$",
                r"^base_.*",
                r".*mixins?$",
                r".*base$",
            ],
            ArchetypeType.DECORATOR: [r".*_dec$", r".*decorator$", r".*wrapper$"],
            ArchetypeType.MARKER: [r"^__.*__$"],
            ArchetypeType.STUB: [r".*_mock$", r".*_stub$", r".*_fake$", r"^mock_.*"],
            ArchetypeType.ASSET: [r".*assets?$", r".*resources?$", r".*templates?$"],
        }
    },
}


def get_scope_registry() -> ScopeRegistry:
    return _SCOPE_REGISTRY


def get_layer_registry() -> LayerRegistry:
    return _LAYER_REGISTRY


def get_direction_registry() -> DirectionRegistry:
    return _DIRECTION_REGISTRY


def get_structural_registry() -> StructuralRegistry:
    return _STRUCTURAL_REGISTRY


def get_naming_registry() -> NamingRegistry:
    return _NAMING_REGISTRY
