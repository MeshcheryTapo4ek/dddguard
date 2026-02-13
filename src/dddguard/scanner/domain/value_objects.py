from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True, slots=True)
class DiscoveredContextVo:
    """
    Value Object representing a discovered Bounded Context within the project.
    """

    context_name: str
    macro_zone: str | None
