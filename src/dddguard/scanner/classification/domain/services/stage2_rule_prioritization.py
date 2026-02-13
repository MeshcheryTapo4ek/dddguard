import functools
from dataclasses import dataclass
from typing import Final

from dddguard.shared.domain import (
    DDD_NAMING_REGISTRY,
    DDD_STRUCTURAL_REGISTRY,
    ComponentType,
    DirectionEnum,
    LayerEnum,
)

# Configuration: Layer Specificity Weights
# Lower value = Higher Priority.
# Specific architectural layers beat generic Global/Undefined layers.
# Marked as Final to prevent accidental modification.
_LAYER_WEIGHTS: Final[dict[LayerEnum, int]] = {
    LayerEnum.COMPOSITION: 0,
    LayerEnum.DOMAIN: 1,
    LayerEnum.APP: 2,
    LayerEnum.ADAPTERS: 3,
    LayerEnum.PORTS: 4,
    LayerEnum.GLOBAL: 10,  # Fallback
    LayerEnum.UNDEFINED: 20,  # Lowest priority
}


@dataclass(frozen=True, slots=True)
class RuleCandidate:
    """DTO representing a prioritized regex rule."""

    comp_type: ComponentType
    regex: str
    weight: int
    origin_layer: LayerEnum


@dataclass(frozen=True, kw_only=True, slots=True)
class Stage2RulePrioritizationService:
    """
    Domain Service: Stage 2 - Rule Prioritization.
    Generates a sorted pool of regex rules applicable to the identified coordinates.
    """

    @staticmethod
    def get_applicable_rules(
        layer: LayerEnum, direction: DirectionEnum
    ) -> tuple[RuleCandidate, ...]:
        """
        Returns a prioritized list of rules applicable to the given coordinates.
        Wrapper around cached static logic.
        """
        return Stage2RulePrioritizationService._build_prioritized_pool(layer, direction)

    @staticmethod
    @functools.lru_cache(maxsize=128)
    def _build_prioritized_pool(
        layer: LayerEnum, direction: DirectionEnum
    ) -> tuple[RuleCandidate, ...]:
        """
        Constructs and sorts the rule list based on Layer Weights and Regex Specificity.
        """
        raw_pool: list[RuleCandidate] = []

        # 1. Determine Target Layers (Current + Global Fallback)
        target_layers = [layer]
        if layer != LayerEnum.GLOBAL:
            target_layers.append(LayerEnum.GLOBAL)

        # 2. Determine Compatible Directions (Exact + ANY + NONE if undefined)
        compatible_directions = {direction, DirectionEnum.ANY}
        if direction == DirectionEnum.UNDEFINED:
            compatible_directions.add(DirectionEnum.NONE)

        # 3. Harvest Rules
        for registry in (DDD_STRUCTURAL_REGISTRY, DDD_NAMING_REGISTRY):
            for target_layer in target_layers:
                layer_data = registry.get(target_layer, {})

                for target_dir, types in layer_data.items():
                    if target_dir not in compatible_directions:
                        continue

                    for comp_type, regexes in types.items():
                        for rx in regexes:
                            raw_pool.append(
                                RuleCandidate(
                                    comp_type=comp_type,
                                    regex=rx,
                                    weight=_LAYER_WEIGHTS.get(target_layer, 99),
                                    origin_layer=target_layer,
                                )
                            )

        # 4. Sort Strategy:
        # Primary: Weight (ASC) -> Specific layers first.
        # Secondary: Regex Length (DESC) -> Stricter/Longer regexes first.
        sorted_pool = sorted(raw_pool, key=lambda r: (r.weight, -len(r.regex)))
        return tuple(sorted_pool)
