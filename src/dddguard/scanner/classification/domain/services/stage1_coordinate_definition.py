import re
from dataclasses import dataclass

from dddguard.shared.domain import DirectionEnum, LayerEnum, ScopeEnum

from .....shared.domain.registry import DDD_DIRECTION_REGISTRY, DDD_LAYER_REGISTRY
from ..value_objects import ContextBoundaryVo, IdentificationCoordinatesVo


@dataclass(frozen=True, kw_only=True, slots=True)
class Stage1CoordinateDefinitionService:
    """
    Domain Service: Stage 1 - Coordinate Definition.

    Refines the raw Boundary detected in Stage 0 into strict architectural coordinates.
    It determines the **Vertical Axis** (Direction) and prepares clean tokens for
    Component Matching (Stage 3).

    Responsibilities:
    1.  **Direction Discovery:** Scans path parts for keywords like 'driving', 'driven', 'api', 'db'.
    2.  **Layer Refinement:** Adjusts Layer inference for special scopes (e.g., ROOT).
    3.  **Noise Filtering:** Removes Layer and Direction tokens from the path, leaving
        only the "Searchable Tokens" (business names or component patterns).
    """

    @staticmethod
    def define_coordinates(boundary: ContextBoundaryVo) -> IdentificationCoordinatesVo:
        """
        Executes the coordinate definition logic.

        :param boundary: The result from Stage 0 containing the Context and Macro info.
        :return: Finalized architectural coordinates (Scope, Layer, Direction) and clean tokens.
        """
        # 1. Determine Direction (Scanning inside effective parts)
        # e.g., parts=("adapters", "driving", "api", "controller.py") -> Direction.DRIVING
        direction, dir_tokens = Stage1CoordinateDefinitionService._discover_direction(
            boundary.effective_parts
        )

        # 2. Refine Layer
        # Handle special case: Files in 'src/root/' often belong to COMPOSITION layer
        # if not explicitly stated otherwise.
        final_layer = boundary.detected_layer_token
        if boundary.scope == ScopeEnum.ROOT and final_layer == LayerEnum.UNDEFINED:
            final_layer = LayerEnum.COMPOSITION

        # 3. Filter Searchable Tokens (Token Distillation)
        # We strip away structural noise (Layer names, Direction names) to focus on the content.
        # e.g. ("ports", "driving", "user_facade.py") -> ("user_facade")
        searchable_tokens: list[str] = []

        for token in boundary.effective_parts:
            # Skip tokens that defined the Direction
            if token in dir_tokens:
                continue

            # Skip tokens that defined the Layer (e.g. "adapters", "ports")
            if Stage1CoordinateDefinitionService._is_layer_token(
                token, boundary.detected_layer_token
            ):
                continue

            searchable_tokens.append(token)

        return IdentificationCoordinatesVo(
            scope=boundary.scope,
            layer=final_layer,
            direction=direction,
            searchable_tokens=searchable_tokens,
        )

    @staticmethod
    def _discover_direction(parts: tuple[str, ...]) -> tuple[DirectionEnum, set[str]]:
        """
        Scans effective path for 'driving' (inbound) or 'driven' (outbound) tokens.
        Returns the Direction enum and the set of tokens that triggered the match.
        """
        for part in parts:
            for direction, regexes in DDD_DIRECTION_REGISTRY.items():
                if any(re.fullmatch(rx, part, re.IGNORECASE) for rx in regexes):
                    return direction, {part}
        return DirectionEnum.UNDEFINED, set()

    @staticmethod
    def _is_layer_token(token: str, layer: LayerEnum) -> bool:
        """
        Checks if a specific path part is the one that triggered the Layer detection.
        Used to filter it out from Searchable Tokens.
        """
        if layer == LayerEnum.UNDEFINED:
            return False

        regexes = DDD_LAYER_REGISTRY.get(layer, [])
        return any(re.fullmatch(rx, token, re.IGNORECASE) for rx in regexes)
