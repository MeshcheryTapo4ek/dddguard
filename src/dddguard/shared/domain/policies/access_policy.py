"""
Architectural Policies (Laws of Physics) for DDD Architecture.
This module defines the strict import allowance matrices used by the Linter.
"""

from typing import Dict, Set, Final
from ..value_objects.architecture_enums import LayerEnum

# ==============================================================================
# 1. INTRA-CONTEXT RULES (Isolation within a single Bounded Context)
# ==============================================================================
# Defines allowed and forbidden imports between layers.

INTERNAL_ACCESS_MATRIX: Final[Dict[LayerEnum, Dict[str, Set[LayerEnum]]]] = {
    # DOMAIN: Pure business logic. Highest level of isolation.
    LayerEnum.DOMAIN: {
        "allowed": {LayerEnum.DOMAIN, LayerEnum.GLOBAL},
        "forbidden": {
            LayerEnum.APP,
            LayerEnum.PORTS,
            LayerEnum.ADAPTERS,
            LayerEnum.COMPOSITION,
        },
    },
    # APP: Orchestration. Coordinates Domain but knows nothing of I/O.
    LayerEnum.APP: {
        "allowed": {LayerEnum.APP, LayerEnum.DOMAIN, LayerEnum.GLOBAL},
        "forbidden": {LayerEnum.PORTS, LayerEnum.ADAPTERS, LayerEnum.COMPOSITION},
    },
    # PORTS: The Bridge. Translates between Tech and Core.
    # PORTS may import Driven Adapters to satisfy interface implementations.
    LayerEnum.PORTS: {
        "allowed": {
            LayerEnum.PORTS,
            LayerEnum.APP,
            LayerEnum.DOMAIN,
            LayerEnum.ADAPTERS,
            LayerEnum.GLOBAL,
        },
        "forbidden": {LayerEnum.COMPOSITION},
    },
    # ADAPTERS: Technology foundation. Must communicate via Ports.
    LayerEnum.ADAPTERS: {
        "allowed": {LayerEnum.ADAPTERS, LayerEnum.PORTS, LayerEnum.GLOBAL},
        "forbidden": {LayerEnum.DOMAIN, LayerEnum.APP, LayerEnum.COMPOSITION},
    },
    # COMPOSITION: The "Glue". Wires everything together.
    LayerEnum.COMPOSITION: {
        "allowed": {
            LayerEnum.COMPOSITION,
            LayerEnum.DOMAIN,
            LayerEnum.APP,
            LayerEnum.PORTS,
            LayerEnum.ADAPTERS,
            LayerEnum.GLOBAL,
        },
        "forbidden": set(),
    },
}

# ==============================================================================
# 2. INTER-CONTEXT RULES (Boundaries between Bounded Contexts)
# ==============================================================================

PUBLIC_LAYERS: Final[Set[LayerEnum]] = {
    LayerEnum.PORTS,
}

OUTBOUND_LAYERS: Final[Set[LayerEnum]] = {
    LayerEnum.PORTS,
}
