"""
Defines the "Laws of Physics" for DDD Architecture.
Who can import whom?
"""
from ..domain.enums import ContextLayerEnum

# ==============================================================================
# 1. INTRA-CONTEXT RULES (Inside one Bounded Context)
# ==============================================================================
INTERNAL_ACCESS_MATRIX = {
    # DOMAIN: Pure Business Logic. Isolated.
    ContextLayerEnum.DOMAIN: {
        "allowed": {ContextLayerEnum.DOMAIN},
        "forbidden": {
            ContextLayerEnum.APP, ContextLayerEnum.DRIVING_ADAPTERS, ContextLayerEnum.DRIVEN_ADAPTERS,
            ContextLayerEnum.DRIVING_PORTS, ContextLayerEnum.DRIVEN_PORTS,
            ContextLayerEnum.DRIVING_DTO, ContextLayerEnum.DRIVEN_DTO,
        },
    },
    # APP: Orchestration. Coordinates Domain.
    ContextLayerEnum.APP: {
        "allowed": {ContextLayerEnum.APP, ContextLayerEnum.DOMAIN},
        "forbidden": {
            ContextLayerEnum.DRIVING_DTO, ContextLayerEnum.DRIVEN_DTO,
            ContextLayerEnum.DRIVING_ADAPTERS, ContextLayerEnum.DRIVEN_ADAPTERS,
            ContextLayerEnum.DRIVING_PORTS, ContextLayerEnum.DRIVEN_PORTS,
        },
    },
    # DRIVING ADAPTERS: Controllers. Convert DTOs -> Domain.
    ContextLayerEnum.DRIVING_ADAPTERS: {
        "allowed": {
            ContextLayerEnum.APP, ContextLayerEnum.DOMAIN,
            ContextLayerEnum.DRIVING_DTO, ContextLayerEnum.DRIVEN_DTO,
        },
        "forbidden": {
            ContextLayerEnum.DRIVEN_ADAPTERS, ContextLayerEnum.DRIVEN_PORTS, ContextLayerEnum.DRIVING_PORTS,
        },
    },
    # DRIVEN ADAPTERS: Repositories/Gateways. Implement App Interfaces.
    ContextLayerEnum.DRIVEN_ADAPTERS: {
        "allowed": {
            ContextLayerEnum.APP, ContextLayerEnum.DOMAIN, ContextLayerEnum.DRIVEN_PORTS,
            ContextLayerEnum.DRIVEN_DTO, ContextLayerEnum.DRIVING_DTO,
        },
        "forbidden": {ContextLayerEnum.DRIVING_ADAPTERS, ContextLayerEnum.DRIVING_PORTS},
    },
    # DTOs: Data Contracts. Dumb objects.
    ContextLayerEnum.DRIVING_DTO: {
        "allowed": {ContextLayerEnum.DOMAIN, ContextLayerEnum.DRIVING_DTO},
        "forbidden": {
            ContextLayerEnum.APP, ContextLayerEnum.DRIVING_ADAPTERS, ContextLayerEnum.DRIVEN_ADAPTERS,
            ContextLayerEnum.DRIVING_PORTS, ContextLayerEnum.DRIVEN_PORTS, ContextLayerEnum.DRIVEN_DTO,
        },
    },
    ContextLayerEnum.DRIVEN_DTO: {
        "allowed": {ContextLayerEnum.DOMAIN, ContextLayerEnum.DRIVEN_DTO},
        "forbidden": {
            ContextLayerEnum.APP, ContextLayerEnum.DRIVING_ADAPTERS, ContextLayerEnum.DRIVEN_ADAPTERS,
            ContextLayerEnum.DRIVING_PORTS, ContextLayerEnum.DRIVEN_PORTS, ContextLayerEnum.DRIVING_DTO,
        },
    },
    # PORTS: Infrastructure Implementation (Frameworks/Drivers)
    ContextLayerEnum.DRIVING_PORTS: {
        "allowed": {ContextLayerEnum.DRIVING_ADAPTERS, ContextLayerEnum.DRIVING_DTO, ContextLayerEnum.DRIVEN_DTO},
        "forbidden": {ContextLayerEnum.DOMAIN, ContextLayerEnum.APP, ContextLayerEnum.DRIVEN_ADAPTERS, ContextLayerEnum.DRIVEN_PORTS},
    },
    ContextLayerEnum.DRIVEN_PORTS: {
        "allowed": {ContextLayerEnum.DRIVEN_DTO},
        "forbidden": {ContextLayerEnum.DOMAIN, ContextLayerEnum.APP, ContextLayerEnum.DRIVING_ADAPTERS, ContextLayerEnum.DRIVEN_ADAPTERS, ContextLayerEnum.DRIVING_PORTS},
    },
}

# ==============================================================================
# 2. INTER-CONTEXT RULES (Between Contexts)
# ==============================================================================

# WHAT can be imported from another context?
PUBLIC_LAYERS = {
    ContextLayerEnum.DRIVING_DTO,
    ContextLayerEnum.DRIVING_ADAPTERS,
}

# WHO can initiate a call to another context?
OUTBOUND_LAYERS = {
    ContextLayerEnum.DRIVEN_ADAPTERS,
}