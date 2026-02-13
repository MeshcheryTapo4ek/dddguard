from enum import Enum, unique


@unique
class ZoneKey(str, Enum):
    """
    Strict constants for visual zones in the architecture tower.
    """

    # 1. Domain (Core)
    DOMAIN = "DOMAIN"

    # 2. Application
    APP = "APP"

    # 3. Adapters (The Split Zone)
    ADAPTERS_DRIVING = "ADAPTERS_DRIVING"
    ADAPTERS_DRIVEN = "ADAPTERS_DRIVEN"
    ADAPTERS_OTHER = "ADAPTERS_OTHER"  # Fallback

    # 4. Ports (The Split Zone)
    PORTS_DRIVING = "PORTS_DRIVING"
    PORTS_DRIVEN = "PORTS_DRIVEN"
    PORTS_OTHER = "PORTS_OTHER"  # Fallback

    # 5. Wiring
    COMPOSITION = "COMPOSITION"

    # 6. Fallback
    OTHER = "OTHER"
