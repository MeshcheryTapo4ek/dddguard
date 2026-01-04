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
    ConfigVo
)


@dataclass(frozen=True, slots=True)
class RuleCandidate:
    """Internal prioritized rule definition."""
    comp_type: ComponentType
    regex: str
    weight: int


@dataclass(frozen=True, kw_only=True, slots=True)
class SrmEngineService:
    """
    SRM v2.0 Engine: Implements 4-stage strict identification.
    Stage -1: Source Root Stripping (New!)
    Stage 0: Path Normalization (Macro Contexts)
    Stage 1: Discovery (Scope/Layer/Direction)
    Stage 2: Filtering & Prioritization
    Stage 3: Structural Match (Folder Tokens)
    Stage 4: Name Match (Filename Stem)
    """

    config: ConfigVo

    def identify(
        self, relative_path_parts: Tuple[str, ...], filename_stem: str
    ) -> ComponentPassport:
        
        # --- Stage -1: SOURCE ROOT STRIPPING ---
        # If the path starts with 'src' (or whatever is configured), strip it.
        # Otherwise, the engine thinks 'src' is the Bounded Context.
        analysis_parts = relative_path_parts
        source_dir = self.config.project.source_dir  # e.g. "src"
        
        if analysis_parts and analysis_parts[0] == source_dir:
            analysis_parts = analysis_parts[1:]

        # --- Stage 0: PATH NORMALIZATION (Macro Contexts) ---
        normalized_parts, macro_zone = self._normalize_path(analysis_parts)

        # --- Stage 1: DISCOVERY ---
        scope, scope_tokens = self._discover_scope(
            normalized_parts[0] if normalized_parts else ""
        )
        layer, layer_tokens = self._discover_layer(normalized_parts, scope)
        direction, dir_tokens = self._discover_direction(normalized_parts)

        # Determine Context Name
        context_name = None
        if scope == ScopeEnum.CONTEXT and normalized_parts:
            # First folder in normalized path is the context name
            # e.g. ("detection", "app", ...) -> context="detection"
            context_name = normalized_parts[0]
        elif scope == ScopeEnum.SHARED:
            context_name = "shared"
        elif scope == ScopeEnum.ROOT:
            context_name = "root"

        # --- Stage 2: FILTERING & PRIORITIZATION ---
        discovery_metadata = scope_tokens | layer_tokens | dir_tokens
        pool = self._get_prioritized_pool(layer, direction)

        # --- Stage 3: STRUCTURAL MATCH ---
        # Search in folders that are NOT used for discovery
        search_folders = [p for p in normalized_parts if p not in discovery_metadata]
        identified_type = self._run_match(pool, search_folders)

        if identified_type != ArchetypeType.UNKNOWN:
            return ComponentPassport(
                scope=scope,
                context_name=context_name,
                macro_zone=macro_zone or "General",
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
            macro_zone=macro_zone, # Can be None if General
            layer=layer,
            direction=direction,
            component_type=identified_type,
            match_method=MatchMethod.NAME
            if identified_type != ArchetypeType.UNKNOWN
            else MatchMethod.UNKNOWN,
        )

    # --- Internals ---

    @staticmethod
    @functools.lru_cache(maxsize=64)
    def _get_prioritized_pool(
        layer: LayerEnum, direction: DirectionEnum
    ) -> Tuple[RuleCandidate, ...]:
        """
        Creates a prioritized rule list based on coordinates.
        Priority: Layer Weight (ASC) -> Regex Length (DESC).
        """
        raw_pool: List[RuleCandidate] = []
        target_layers = [layer, LayerEnum.GLOBAL]
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
        # Then by regex length (longer = more specific = higher priority)
        sorted_pool = sorted(raw_pool, key=lambda r: (r.weight, -len(r.regex)))
        return tuple(sorted_pool)

    def _normalize_path(
        self, parts: Tuple[str, ...]
    ) -> Tuple[Tuple[str, ...], str | None]:
        """
        Checks against configured macro contexts.
        Returns (effective_parts, macro_zone_tag).
        """
        if not parts:
            return parts, None

        root_folder = parts[0]
        # Config map: { "ZoneTag": "PhysicalDir" } e.g. {"scanner": "scanner"}
        if self.config.project and self.config.project.macro_contexts:
            for zone_tag, physical_dir in self.config.project.macro_contexts.items():
                if physical_dir == root_folder:
                    # MATCH FOUND: Strip the macro folder from the analysis path
                    # e.g. ("scanner", "detection", "domain") -> ("detection", "domain")
                    # macro_zone = "scanner"
                    return parts[1:], zone_tag

        return parts, None
    
    def _run_match(
        self, pool: Iterable[RuleCandidate], tokens: List[str]
    ) -> ComponentType:
        """
        Performs strict Full Match against provided tokens.
        """
        for rule in pool:
            for token in tokens:
                if re.fullmatch(rule.regex, token, re.IGNORECASE):
                    return rule.comp_type
        return ArchetypeType.UNKNOWN

    def _discover_scope(self, root_token: str) -> Tuple[ScopeEnum, Set[str]]:
        for scope, regexes in DDD_SCOPE_REGISTRY.items():
            if any(re.fullmatch(rx, root_token, re.IGNORECASE) for rx in regexes):
                return scope, {root_token}
        return ScopeEnum.CONTEXT, {root_token}

    def _discover_layer(
        self, parts: Tuple[str, ...], scope: ScopeEnum
    ) -> Tuple[LayerEnum, Set[str]]:
        for part in parts:
            for layer, regexes in DDD_LAYER_REGISTRY.items():
                if any(re.fullmatch(rx, part, re.IGNORECASE) for rx in regexes):
                    return layer, {part}

        # Fallback Logic
        if scope == ScopeEnum.CONTEXT:
            # If we are deep in a context but found no layer, assume Adapters (Tech) or Undefined
            # For strictness, return UNDEFINED unless forced otherwise
            return LayerEnum.UNDEFINED, set()

        return LayerEnum.UNDEFINED, set()

    def _discover_direction(
        self, parts: Tuple[str, ...]
    ) -> Tuple[DirectionEnum, Set[str]]:
        for part in parts:
            for direction, regexes in DDD_DIRECTION_REGISTRY.items():
                if any(re.fullmatch(rx, part, re.IGNORECASE) for rx in regexes):
                    return direction, {part}
        return DirectionEnum.UNDEFINED, set()