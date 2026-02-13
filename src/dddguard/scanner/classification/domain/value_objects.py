from dataclasses import dataclass

from dddguard.shared.domain import (
    DirectionEnum,
    LayerEnum,
    ScopeEnum,
)


@dataclass(frozen=True, kw_only=True, slots=True)
class ContextBoundaryVo:
    """
    Result of Stage 0: Context Boundary Detection.
    Internal to Classification Pipeline.
    """

    scope: ScopeEnum
    macro_path: str | None
    context_name: str | None
    effective_parts: tuple[str, ...]
    detected_layer_token: LayerEnum


@dataclass(frozen=True, kw_only=True, slots=True)
class IdentificationCoordinatesVo:
    """
    Result of Stage 1: Coordinate Definition.
    Internal to Classification Pipeline.
    """

    scope: ScopeEnum
    layer: LayerEnum
    direction: DirectionEnum
    searchable_tokens: list[str]
