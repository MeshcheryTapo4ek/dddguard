from typing import Final, Literal

from typing_extensions import TypedDict

from ..domain.architecture_enums import DirectionEnum, LayerEnum

# ==============================================================================
# TYPE DEFINITIONS
# ==============================================================================


class AccessRule(TypedDict):
    """Typed structure for layer access rules."""

    allowed: frozenset[tuple[LayerEnum, DirectionEnum]]
    forbidden: frozenset[tuple[LayerEnum, DirectionEnum]]


# Key for the access matrix: (Layer, Direction)
LayerDirectionKey = tuple[LayerEnum, DirectionEnum]

# Type alias for the full internal access matrix
InternalAccessMatrix = dict[LayerDirectionKey, AccessRule]

# Rule names (replacing opaque codes like R100, F101, C201)
RuleName = Literal[
    "Domain Purity",
    "App Isolation",
    "Driving Port Boundary",
    "Driven Port Boundary",
    "Driving Adapter Boundary",
    "Driven Adapter Boundary",
    "Fractal Upstream Access",
    "Fractal Downstream Access",
    "Cross-Context Outbound",
    "Cross-Context Inbound",
    "Shared Independence",
    "Root Isolation",
]


# ==============================================================================
# HELPER: Wildcard Direction Expander
# ==============================================================================


def _expand_layer(
    layer: LayerEnum, direction: DirectionEnum = DirectionEnum.ANY
) -> frozenset[tuple[LayerEnum, DirectionEnum]]:
    """
    Expands a layer specification into concrete (Layer, Direction) tuples.

    If direction is ANY, expands to DRIVING, DRIVEN, NONE.
    If direction is NONE, expands to NONE only (for Domain, App, Composition, Global).
    """
    if direction == DirectionEnum.ANY:
        return frozenset(
            {
                (layer, DirectionEnum.DRIVING),
                (layer, DirectionEnum.DRIVEN),
                (layer, DirectionEnum.NONE),
            }
        )
    return frozenset({(layer, direction)})


# ==============================================================================
# GROUP 1: INTERNAL RULES (Same Context)
# ==============================================================================

# Rules 1-7: Layer-to-Layer dependencies within a single bounded context.
# Key = (Source Layer, Source Direction)
# Value = { allowed: set of (Target Layer, Target Direction), forbidden: ... }

INTERNAL_ACCESS_MATRIX: Final[InternalAccessMatrix] = {
    # --- DOMAIN LAYER (no direction subdivision) ---
    # Rule 1: Domain Purity
    # Domain can only import Domain and Global
    (LayerEnum.DOMAIN, DirectionEnum.NONE): AccessRule(
        allowed=_expand_layer(LayerEnum.DOMAIN, DirectionEnum.NONE)
        | _expand_layer(LayerEnum.GLOBAL, DirectionEnum.ANY),
        forbidden=_expand_layer(LayerEnum.APP, DirectionEnum.NONE)
        | _expand_layer(LayerEnum.PORTS, DirectionEnum.ANY)
        | _expand_layer(LayerEnum.ADAPTERS, DirectionEnum.ANY)
        | _expand_layer(LayerEnum.COMPOSITION, DirectionEnum.NONE),
    ),
    # --- APP LAYER (no direction subdivision) ---
    # Rule 2: App Isolation
    # App can import App (interfaces), Domain, Global
    (LayerEnum.APP, DirectionEnum.NONE): AccessRule(
        allowed=_expand_layer(LayerEnum.APP, DirectionEnum.NONE)
        | _expand_layer(LayerEnum.DOMAIN, DirectionEnum.NONE)
        | _expand_layer(LayerEnum.GLOBAL, DirectionEnum.ANY),
        forbidden=_expand_layer(LayerEnum.PORTS, DirectionEnum.ANY)
        | _expand_layer(LayerEnum.ADAPTERS, DirectionEnum.ANY)
        | _expand_layer(LayerEnum.COMPOSITION, DirectionEnum.NONE),
    ),
    # --- PORTS LAYER (subdivided by direction) ---
    # Rule 3: Driving Port Boundary
    # Ports/Driving can import App, Domain, Ports/Driving (schemas), Global
    (LayerEnum.PORTS, DirectionEnum.DRIVING): AccessRule(
        allowed=_expand_layer(LayerEnum.APP, DirectionEnum.NONE)
        | _expand_layer(LayerEnum.DOMAIN, DirectionEnum.NONE)
        | _expand_layer(LayerEnum.PORTS, DirectionEnum.DRIVING)
        | _expand_layer(LayerEnum.GLOBAL, DirectionEnum.ANY),
        forbidden=_expand_layer(LayerEnum.PORTS, DirectionEnum.DRIVEN)
        | _expand_layer(LayerEnum.ADAPTERS, DirectionEnum.ANY)
        | _expand_layer(LayerEnum.COMPOSITION, DirectionEnum.NONE),
    ),
    # Rule 4: Driven Port Boundary
    # Ports/Driven can import App (interfaces), Domain, Adapters/Driven (tools), Global
    (LayerEnum.PORTS, DirectionEnum.DRIVEN): AccessRule(
        allowed=_expand_layer(LayerEnum.APP, DirectionEnum.NONE)
        | _expand_layer(LayerEnum.DOMAIN, DirectionEnum.NONE)
        | _expand_layer(LayerEnum.ADAPTERS, DirectionEnum.DRIVEN)
        | _expand_layer(LayerEnum.GLOBAL, DirectionEnum.ANY),
        forbidden=_expand_layer(LayerEnum.PORTS, DirectionEnum.DRIVING)
        | _expand_layer(LayerEnum.ADAPTERS, DirectionEnum.DRIVING)
        | _expand_layer(LayerEnum.COMPOSITION, DirectionEnum.NONE),
    ),
    # --- ADAPTERS LAYER (subdivided by direction) ---
    # Rule 5: Driving Adapter Boundary
    # Adapters/Driving can import Ports/Driving (facades, schemas), Global
    (LayerEnum.ADAPTERS, DirectionEnum.DRIVING): AccessRule(
        allowed=_expand_layer(LayerEnum.PORTS, DirectionEnum.DRIVING)
        | _expand_layer(LayerEnum.GLOBAL, DirectionEnum.ANY),
        forbidden=_expand_layer(LayerEnum.DOMAIN, DirectionEnum.NONE)
        | _expand_layer(LayerEnum.APP, DirectionEnum.NONE)
        | _expand_layer(LayerEnum.PORTS, DirectionEnum.DRIVEN)
        | _expand_layer(LayerEnum.ADAPTERS, DirectionEnum.DRIVEN)
        | _expand_layer(LayerEnum.COMPOSITION, DirectionEnum.NONE),
    ),
    # Rule 6: Driven Adapter Boundary
    # Adapters/Driven can import Global, Shared only (pure infrastructure)
    (LayerEnum.ADAPTERS, DirectionEnum.DRIVEN): AccessRule(
        allowed=_expand_layer(LayerEnum.GLOBAL, DirectionEnum.ANY),
        forbidden=_expand_layer(LayerEnum.DOMAIN, DirectionEnum.NONE)
        | _expand_layer(LayerEnum.APP, DirectionEnum.NONE)
        | _expand_layer(LayerEnum.PORTS, DirectionEnum.ANY)
        | _expand_layer(LayerEnum.ADAPTERS, DirectionEnum.DRIVING)
        | _expand_layer(LayerEnum.COMPOSITION, DirectionEnum.NONE),
    ),
    # --- COMPOSITION LAYER (no direction subdivision) ---
    # Rule 7: Composition (bypassed in rule engine — can import everything within context)
    (LayerEnum.COMPOSITION, DirectionEnum.NONE): AccessRule(
        allowed=_expand_layer(LayerEnum.DOMAIN, DirectionEnum.NONE)
        | _expand_layer(LayerEnum.APP, DirectionEnum.NONE)
        | _expand_layer(LayerEnum.PORTS, DirectionEnum.ANY)
        | _expand_layer(LayerEnum.ADAPTERS, DirectionEnum.ANY)
        | _expand_layer(LayerEnum.COMPOSITION, DirectionEnum.NONE)
        | _expand_layer(LayerEnum.GLOBAL, DirectionEnum.ANY),
        forbidden=frozenset(),
    ),
}


# ==============================================================================
# GROUP 2: FRACTAL RULES (Parent ↔ Child Contexts)
# ==============================================================================

# Rule 8: Fractal Upstream Access (Child -> Parent)
# Child can import: Domain, App, Ports/Driven
FRACTAL_UPSTREAM_ALLOWED: Final[frozenset[LayerDirectionKey]] = (
    _expand_layer(LayerEnum.DOMAIN, DirectionEnum.NONE)
    | _expand_layer(LayerEnum.APP, DirectionEnum.NONE)
    | _expand_layer(LayerEnum.PORTS, DirectionEnum.DRIVEN)
    | _expand_layer(LayerEnum.GLOBAL, DirectionEnum.ANY)
)

FRACTAL_UPSTREAM_FORBIDDEN: Final[frozenset[LayerDirectionKey]] = (
    _expand_layer(LayerEnum.PORTS, DirectionEnum.DRIVING)
    | _expand_layer(LayerEnum.ADAPTERS, DirectionEnum.ANY)
    | _expand_layer(LayerEnum.COMPOSITION, DirectionEnum.NONE)
)

# Rule 9: Fractal Downstream Access (Parent -> Child)
# Parent can import: Ports/Driving only (facades)
FRACTAL_DOWNSTREAM_ALLOWED: Final[frozenset[LayerDirectionKey]] = _expand_layer(
    LayerEnum.PORTS, DirectionEnum.DRIVING
)

FRACTAL_DOWNSTREAM_FORBIDDEN: Final[frozenset[LayerDirectionKey]] = (
    _expand_layer(LayerEnum.DOMAIN, DirectionEnum.NONE)
    | _expand_layer(LayerEnum.APP, DirectionEnum.NONE)
    | _expand_layer(LayerEnum.PORTS, DirectionEnum.DRIVEN)
    | _expand_layer(LayerEnum.ADAPTERS, DirectionEnum.ANY)
    | _expand_layer(LayerEnum.COMPOSITION, DirectionEnum.NONE)
)


# ==============================================================================
# GROUP 3: CROSS-CONTEXT RULES (Alien Contexts)
# ==============================================================================

# Rule 10: Cross-Context Outbound
# Only Ports/Driven (ACL) can initiate calls to other contexts
CROSS_CONTEXT_OUTBOUND_ALLOWED: Final[frozenset[LayerDirectionKey]] = _expand_layer(
    LayerEnum.PORTS, DirectionEnum.DRIVEN
)

# Rule 11: Cross-Context Inbound
# Can only call Ports/Driving of other contexts
CROSS_CONTEXT_INBOUND_ALLOWED: Final[frozenset[LayerDirectionKey]] = _expand_layer(
    LayerEnum.PORTS, DirectionEnum.DRIVING
)


# ==============================================================================
# BYPASS CONDITIONS
# ==============================================================================

# Layers that can import anything within their own context (bypass internal rules)
COMPOSITION_LAYERS: Final[frozenset[LayerEnum]] = frozenset(
    {
        LayerEnum.COMPOSITION,
        LayerEnum.GLOBAL,
    }
)
