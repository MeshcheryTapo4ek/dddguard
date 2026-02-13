from ..assets.ddd_rules_data import (
    DirectionRegistry,
    LayerRegistry,
    NamingRegistry,
    ScopeRegistry,
    StructuralRegistry,
    get_direction_registry,
    get_layer_registry,
    get_naming_registry,
    get_scope_registry,
    get_structural_registry,
)

DDD_SCOPE_REGISTRY: ScopeRegistry = get_scope_registry()

DDD_LAYER_REGISTRY: LayerRegistry = get_layer_registry()

DDD_DIRECTION_REGISTRY: DirectionRegistry = get_direction_registry()

DDD_STRUCTURAL_REGISTRY: StructuralRegistry = get_structural_registry()

DDD_NAMING_REGISTRY: NamingRegistry = get_naming_registry()
