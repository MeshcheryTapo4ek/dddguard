import re
import functools
from dataclasses import dataclass
from typing import Tuple, List, Set, Iterable

from dddguard.shared.domain import (
    DDD_SCOPE_REGISTRY,
    DDD_LAYER_REGISTRY,
    DDD_DIRECTION_REGISTRY,
    DDD_STRUCTURAL_REGISTRY,
    DDD_NAMING_REGISTRY,
    ComponentPassport,
    ScopeEnum,
    LayerEnum,
    DirectionEnum,
    MatchMethod,
    LAYER_WEIGHTS,
    ComponentType,
    ArchetypeType,
)


@dataclass(frozen=True, slots=True)
class RuleCandidate:
    """
    Internal prioritized rule definition.
    Uses strict Enum typing for comp_type.
    """

    comp_type: ComponentType
    regex: str
    weight: int


@dataclass(frozen=True, kw_only=True, slots=True)
class SrmEngineService:
    """
    SRM v2.0 Engine: Implements 4-stage strict identification.
    1. Discovery (Scope/Layer/Direction)
    2. Filtering & Prioritization
    3. Structural Match (Folder Tokens)
    4. Name Match (Filename Stem)
    """

    def identify(
        self, relative_path_parts: Tuple[str, ...], filename_stem: str
    ) -> ComponentPassport:
        # --- Stage 1: DISCOVERY ---
        scope, scope_tokens = self._discover_scope(
            relative_path_parts[0] if relative_path_parts else ""
        )
        layer, layer_tokens = self._discover_layer(relative_path_parts)
        direction, dir_tokens = self._discover_direction(relative_path_parts)

        context_name = (
            relative_path_parts[0]
            if scope == ScopeEnum.CONTEXT and relative_path_parts
            else None
        )

        discovery_metadata = scope_tokens | layer_tokens | dir_tokens
        pool = self._get_prioritized_pool(layer, direction)

        # --- Stage 3: STRUCTURAL MATCH ---
        search_folders = [p for p in relative_path_parts if p not in discovery_metadata]
        identified_type = self._run_match(pool, search_folders)

        if identified_type != ArchetypeType.UNKNOWN:
            return ComponentPassport(
                scope=scope,
                context_name=context_name,
                layer=layer,
                direction=direction,
                component_type=identified_type,
                match_method=MatchMethod.STRUCTURAL,
            )

        # --- Stage 4: NAME MATCH ---
        identified_type = self._run_match(pool, [filename_stem])

        return ComponentPassport(
            scope=scope,
            context_name=context_name,
            layer=layer,
            direction=direction,
            component_type=identified_type,
            match_method=MatchMethod.NAME
            if identified_type != ArchetypeType.UNKNOWN
            else MatchMethod.UNKNOWN,
        )

    @functools.lru_cache(maxsize=64)
    def _get_prioritized_pool(
        self, layer: LayerEnum, direction: DirectionEnum
    ) -> Tuple[RuleCandidate, ...]:
        """
        Creates a prioritized rule list based on coordinates.
        Priority logic: Layer Weight (ASC) -> Regex Length (DESC).
        """
        raw_pool: List[RuleCandidate] = []
        # Rules pool includes specific layer and global archetypes
        target_layers = [layer, LayerEnum.GLOBAL]

        # Directions matrix compatibility
        compatible_directions = {direction, DirectionEnum.ANY, DirectionEnum.NONE}

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
                                    weight=LAYER_WEIGHTS.get(target_layer, 99),
                                )
                            )

        # Sort: Composition > Domain > App > Adapters > Ports > Global
        sorted_pool = sorted(raw_pool, key=lambda r: (r.weight, -len(r.regex)))
        return tuple(sorted_pool)

    def _run_match(
        self, pool: Iterable[RuleCandidate], tokens: List[str]
    ) -> ComponentType:
        """
        Performs strict Full Match against provided tokens.
        Adheres to 'implicitly wraps in ^...$' rule via re.fullmatch.
        """
        for rule in pool:
            for token in tokens:
                if re.fullmatch(rule.regex, token, re.IGNORECASE):
                    return rule.comp_type
        return ArchetypeType.UNKNOWN

    # --- Discovery Helpers (Stage 1) ---

    def _discover_scope(self, root_token: str) -> Tuple[ScopeEnum, Set[str]]:
        """Determines scope from first folder."""
        for scope, regexes in DDD_SCOPE_REGISTRY.items():
            if any(re.fullmatch(rx, root_token, re.IGNORECASE) for rx in regexes):
                return scope, {root_token}
        return ScopeEnum.CONTEXT, {root_token}

    def _discover_layer(self, parts: Tuple[str, ...]) -> Tuple[LayerEnum, Set[str]]:
        """Identifies layer based on layer identification markers."""
        for part in parts:
            for layer, regexes in DDD_LAYER_REGISTRY.items():
                if any(re.fullmatch(rx, part, re.IGNORECASE) for rx in regexes):
                    return layer, {part}
        return LayerEnum.UNDEFINED, set()

    def _discover_direction(
        self, parts: Tuple[str, ...]
    ) -> Tuple[DirectionEnum, Set[str]]:
        """Identifies driving/driven direction."""
        for part in parts:
            for direction, regexes in DDD_DIRECTION_REGISTRY.items():
                if any(re.fullmatch(rx, part, re.IGNORECASE) for rx in regexes):
                    return direction, {part}
        return DirectionEnum.UNDEFINED, set()
