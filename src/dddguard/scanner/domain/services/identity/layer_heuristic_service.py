from dataclasses import dataclass, field
from typing import Tuple, Optional, Dict, Set

from dddguard.shared import (
    ContextLayerEnum,
    AnyComponentType,
    AppTypeEnum,
    DomainTypeEnum,
    DrivenAdapterEnum, 
)
from dddguard.shared.assets import get_flat_token_map

@dataclass(frozen=True, kw_only=True, slots=True)
class LayerHeuristicService:
    """
    Domain Service: Level 2 - Fast path token analysis.
    Identifies layer and component type based on folder names and tokens.
    """

    _token_map: Dict[str, Tuple[ContextLayerEnum, AnyComponentType]] = field(
        default_factory=get_flat_token_map, 
        init=False, 
        repr=False
    )

    def analyze(
        self, path_parts: Tuple[str, ...]
    ) -> Tuple[Optional[ContextLayerEnum], Optional[AnyComponentType]]:
        tokens = set(p.lower() for p in path_parts)
        path_str = "/".join(path_parts).lower()

        # 1. Detect Layer (Strict Path check)
        layer = self._detect_layer(path_str, tokens)

        # 2. Detect Type (Context-aware)
        if layer:
            return self._resolve_type_in_layer(layer, tokens)

        # 3. Fallback: Global Token Search (Low confidence)
        for token in tokens:
            if token in self._token_map:
                return self._token_map[token]

        return None, None

    def _detect_layer(self, path_str: str, tokens: Set[str]) -> Optional[ContextLayerEnum]:
        """Determines layer based on directory structure."""
        
        # --- ADAPTERS ---
        if "adapters" in tokens:
            if self._is_driven(path_str): return ContextLayerEnum.DRIVEN_ADAPTERS
            if self._is_driving(path_str): return ContextLayerEnum.DRIVING_ADAPTERS
            return None

        # --- PORTS ---
        if "ports" in tokens:
            if self._is_driven(path_str): return ContextLayerEnum.DRIVEN_PORTS
            if self._is_driving(path_str): return ContextLayerEnum.DRIVING_PORTS
            return ContextLayerEnum.OTHER

        # --- DTOs ---
        if "dto" in tokens or "dtos" in tokens:
            if self._is_driven(path_str): return ContextLayerEnum.DRIVEN_DTO
            if self._is_driving(path_str): return ContextLayerEnum.DRIVING_DTO
            return ContextLayerEnum.DRIVING_DTO 

        # --- CORE ---
        if "domain" in tokens: return ContextLayerEnum.DOMAIN
        if "app" in tokens or "application" in tokens: return ContextLayerEnum.APP
        if "composition" in tokens: return ContextLayerEnum.COMPOSITION
        
        return None

    def _resolve_type_in_layer(
        self, layer: ContextLayerEnum, tokens: Set[str]
    ) -> Tuple[ContextLayerEnum, Optional[AnyComponentType]]:
        """Finds component type valid for the already identified layer."""
        
        # Special handling for ambiguous tokens (Errors)
        if "errors" in tokens or "exceptions" in tokens:
            if layer == ContextLayerEnum.APP: 
                return layer, AppTypeEnum.APP_ERROR
            if layer == ContextLayerEnum.DOMAIN: 
                return layer, DomainTypeEnum.DOMAIN_ERROR
            if layer in (ContextLayerEnum.DRIVEN_ADAPTERS, ContextLayerEnum.DRIVING_ADAPTERS):
                return layer, DrivenAdapterEnum.ADAPTER_ERROR 

        # Lookup in flat map and verify layer match
        for token in tokens:
            if token in self._token_map:
                mapped_layer, mapped_type = self._token_map[token]
                if mapped_layer == layer:
                    return layer, mapped_type
        
        return layer, None

    def _is_driven(self, path: str) -> bool:
        return "driven" in path or "outbound" in path

    def _is_driving(self, path: str) -> bool:
        return "driving" in path or "inbound" in path