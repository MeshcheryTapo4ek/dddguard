# Shared Public API
from .domain import (
    DDD_SCOPE_REGISTRY,
    DDD_LAYER_REGISTRY,
    DDD_DIRECTION_REGISTRY,
    DDD_STRUCTURAL_REGISTRY,
    DDD_NAMING_REGISTRY,
    ComponentPassport,
    ScopeEnum,
    LayerEnum,
    DirectionEnum,
    LAYER_WEIGHTS,
    DomainType,
    AppType,
    PortType,
    AdapterType,
    CompositionType,
    ArchetypeType,
    ComponentType,
    MatchMethod,
    ConfigVo,
    ProjectConfig,
    ScannerConfig,
    INTERNAL_ACCESS_MATRIX,
    PUBLIC_LAYERS,
    OUTBOUND_LAYERS,
)

# Adapters (Driving) - UI & Console Tools
from .adapters.driving.console.dashboard import (
    render_dashboard,
    render_config_info,
    print_no_config_warning,
)
from .adapters.driving.console.widgets import (
    ask_select,
    ask_path,
    ask_text,
    ask_confirm,
    ask_multiselect,
)
from .adapters.driving.console.themes import (
    SCANNER_THEME,
    LINTER_THEME,
    SCAFFOLDER_THEME,
    VISUALIZER_THEME,
    DEFAULT_THEME,
    ROOT_THEME,
    GuardTheme,
)
from .adapters.driving.console.error_handling import safe_execution

# Adapters (Driven) - Infrastructure
from .adapters.driven.files.yaml_config_provider import YamlConfigLoader

# Assets (Help Text, Legends)
from .adapters.driving.console.assets import (
    get_architecture_legend,
    get_naming_cloud_html,
    LINTER_CLI_HELP,
    get_linter_help_renderable,
)

# Composition
from .composition.config_provider import SharedConfigProvider

__all__ = [
    # Enums
    "ScopeEnum",
    "LayerEnum",
    "DirectionEnum",
    "LAYER_WEIGHTS",
    "DomainType",
    "AppType",
    "PortType",
    "AdapterType",
    "CompositionType",
    "ArchetypeType",
    "ComponentType",
    "MatchMethod",
    # Registries
    "DDD_SCOPE_REGISTRY",
    "DDD_LAYER_REGISTRY",
    "DDD_DIRECTION_REGISTRY",
    "DDD_STRUCTURAL_REGISTRY",
    "DDD_NAMING_REGISTRY",
    "ComponentPassport",
    # Config VOs
    "ConfigVo",
    "ProjectConfig",
    "ScannerConfig",
    # Rules
    "INTERNAL_ACCESS_MATRIX",
    "PUBLIC_LAYERS",
    "OUTBOUND_LAYERS",
    # Adapters (Driving)
    "render_dashboard",
    "render_config_info",
    "print_no_config_warning",
    "ask_select",
    "ask_path",
    "ask_text",
    "ask_confirm",
    "ask_multiselect",
    "SCANNER_THEME",
    "LINTER_THEME",
    "SCAFFOLDER_THEME",
    "VISUALIZER_THEME",
    "DEFAULT_THEME",
    "ROOT_THEME",
    "GuardTheme",
    "safe_execution",
    # Adapters (Driven)
    "YamlConfigLoader",
    # Assets
    "get_architecture_legend",
    "get_naming_cloud_html",
    "LINTER_CLI_HELP",
    "get_linter_help_renderable",
    # Composition
    "SharedConfigProvider",
]
