import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Union

from dddguard.scanner import ScannerController, ScanResponseSchema
from dddguard.shared import (
    ScopeEnum, 
    LayerEnum,
    ComponentType,
    ArchetypeType,
    DomainType,
    AppType,
    PortType,
    AdapterType,
    CompositionType
)

# Local Domain Objects
from ....domain import DependencyGraph, DependencyNode, DependencyLink

from ....app import IScannerGateway
from .errors import ScannerIntegrationError

# Initialize module-level logger
logger = logging.getLogger(__name__)

@dataclass(frozen=True, kw_only=True, slots=True)
class ScannerAcl(IScannerGateway):
    """
    Driven Adapter (ACL): Anti-Corruption Layer.
    Translates loose string data from Scanner into strict Enums for Visualizer Domain.
    """

    controller: ScannerController

    # --- ALIAS MAPS (Knowledge about Scanner's flexible naming) ---
    _LAYER_ALIASES = {
        "APPLICATION": LayerEnum.APP,
        "APP": LayerEnum.APP,
        "INFRASTRUCTURE": LayerEnum.ADAPTERS,
        "INFRA": LayerEnum.ADAPTERS,
        "ADAPTERS": LayerEnum.ADAPTERS,
        "INTERFACE": LayerEnum.PORTS,  # Common confusion point
        "INTERFACES": LayerEnum.PORTS,
        "WIRING": LayerEnum.COMPOSITION,
        "BOOTSTRAP": LayerEnum.COMPOSITION,
        "DI": LayerEnum.COMPOSITION,
    }

    def get_dependency_graph(self, root_path: Path) -> DependencyGraph:
        logger.info(f"ACL: Requesting dependency graph from Scanner for: {root_path}")
        try:
            # FIX: Updated call signature to match new ScannerController API.
            # Removed 'show_root' and 'show_shared' arguments.
            response: ScanResponseSchema = self.controller.scan_project(
                target_path=root_path, 
                scan_all=False
            )
            
            logger.debug(
                f"ACL: Received ScanResponse. Contexts: {response.context_count}, Files: {response.file_count}"
            )
            
            graph = self._map_schema_to_domain(response.dependency_graph)
            logger.info(f"ACL: Successfully mapped {len(graph.nodes)} nodes to Domain Graph.")
            return graph

        except Exception as e:
            logger.error(f"ACL: Integration failed: {e}", exc_info=True)
            raise ScannerIntegrationError(
                original_error=f"Unexpected ACL error: {e}"
            ) from e

    def _map_schema_to_domain(self, graph_dict: Dict[str, Any]) -> DependencyGraph:
        nodes: Dict[str, DependencyNode] = {}

        for context_name, layers in graph_dict.items():
            for layer_name, modules in layers.items():
                for mod_data in modules:
                    # 1. Map Imports
                    mapped_imports = []
                    for imp in mod_data.get("imports", []):
                        mapped_imports.append(
                            DependencyLink(
                                source_module=mod_data.get("module", ""),
                                target_module=imp.get("module", ""),
                                target_context=imp.get("context"),
                                target_layer=imp.get("layer"),
                                target_type=imp.get("type"),
                            )
                        )

                    # 2. Smart Resolve Component Type
                    raw_type = mod_data.get("type", "UNKNOWN")
                    comp_type = self._smart_resolve_component_type(raw_type)

                    # 3. Smart Resolve Layer
                    # Use the outer loop key (layer_name) or the internal data
                    raw_layer = mod_data.get("layer") or layer_name
                    layer_enum = self._smart_resolve_layer(raw_layer)

                    # 4. Determine Scope
                    scope = ScopeEnum.CONTEXT
                    if context_name == "shared":
                        scope = ScopeEnum.SHARED
                    elif context_name == "root":
                        scope = ScopeEnum.ROOT

                    module_path = mod_data.get("module", "")
                    
                    node = DependencyNode(
                        module_path=module_path,
                        context=context_name,
                        layer=layer_enum,
                        component_type=comp_type,
                        scope=scope,
                        imports=mapped_imports,
                    )
                    nodes[module_path] = node

        return DependencyGraph(nodes=nodes)

    def _smart_resolve_layer(self, layer_str: str) -> LayerEnum:
        """
        Robustly converts a string to LayerEnum using heuristics and aliases.
        """
        if not layer_str:
            return LayerEnum.UNDEFINED
            
        # FIX: Handle "LayerEnum.APP" format by stripping prefix
        if "." in layer_str:
            layer_str = layer_str.split(".")[-1]

        normalized = str(layer_str).upper().strip()
        
        # 1. Check strict Enum match (Value or Name)
        try:
            return LayerEnum(normalized)
        except ValueError:
            pass
            
        # 2. Check Alias Map
        if normalized in self._LAYER_ALIASES:
            res = self._LAYER_ALIASES[normalized]
            logger.debug(f"ACL: Layer Alias Match -> '{layer_str}' resolved to {res}")
            return res
            
        # 3. Fallback: try matching member names directly if values differ
        if normalized in LayerEnum.__members__:
            return LayerEnum[normalized]

        logger.warning(f"ACL: Could not resolve Layer '{layer_str}' (Norm: {normalized}). Defaulting to UNDEFINED.")
        return LayerEnum.UNDEFINED

    def _smart_resolve_component_type(self, type_str: str) -> Union[ComponentType, str]:
        """
        Iterates through all architectural type registries to find a match.
        """
        if not type_str:
            return ArchetypeType.UNKNOWN

        # FIX: Handle "AppType.USE_CASE" format by stripping prefix
        if "." in type_str:
            type_str = type_str.split(".")[-1]

        normalized = str(type_str).upper().strip()
        
        # Priority order for checking Enums
        registries = [
            DomainType,
            AppType,
            PortType,
            AdapterType,
            CompositionType,
            ArchetypeType
        ]

        for registry in registries:
            # 1. Try Value Match (e.g. "USE_CASE")
            try:
                return registry(normalized)
            except ValueError:
                pass
            
            # 2. Try Key/Member Match (e.g. "USE_CASE" member for value "USE_CASE")
            if normalized in registry.__members__:
                return registry[normalized]
        
        # If unknown, return string so we don't lose data
        if normalized != "UNKNOWN":
             logger.debug(f"ACL: Unknown component type '{type_str}'. Returning raw string.")
             
        return type_str