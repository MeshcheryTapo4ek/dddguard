from dataclasses import dataclass

from dddguard.shared import (
    LayerEnum,
    DirectionEnum,
    AppType,
    DomainType,
)
from ....domain import DependencyNode


@dataclass(frozen=True, kw_only=True, slots=True)
class NodePlacementService:
    """
    Domain Service: Determines the Zone key for a node.
    Restores DRIVING/DRIVEN suffixes for PORTS and ADAPTERS to enable split layouts.
    """

    def get_placement(self, node: DependencyNode) -> str:
        """
        Returns: ZoneKey (e.g., "ADAPTERS_DRIVING", "DOMAIN", "PORTS_OTHER")
        """
        layer = node.layer
        direction = self._infer_direction(node)

        # 1. ADAPTERS
        if layer == LayerEnum.ADAPTERS:
            if direction == DirectionEnum.DRIVING:
                return "ADAPTERS_DRIVING"
            if direction == DirectionEnum.DRIVEN:
                return "ADAPTERS_DRIVEN"
            return "ADAPTERS_OTHER"

        # 2. PORTS
        if layer == LayerEnum.PORTS:
            if direction == DirectionEnum.DRIVING:
                return "PORTS_DRIVING"
            if direction == DirectionEnum.DRIVEN:
                return "PORTS_DRIVEN"
            return "PORTS_OTHER"

        # 3. APP (Application)
        if layer == LayerEnum.APP:
            return "APP"

        # 4. DOMAIN (Core)
        if layer == LayerEnum.DOMAIN:
            return "DOMAIN"

        # 5. COMPOSITION
        if layer == LayerEnum.COMPOSITION:
            return "COMPOSITION"
        
        return "OTHER"

    def _infer_direction(self, node: DependencyNode) -> DirectionEnum:
        """
        Helper to recover direction from the node's metadata if not explicitly stored.
        """
        # Heuristic: check path tokens
        path = node.module_path.lower()
        if ".driving." in path or ".inbound." in path:
            return DirectionEnum.DRIVING
        if ".driven." in path or ".outbound." in path:
            return DirectionEnum.DRIVEN
        
        # Heuristic: check known types
        ctype = str(node.component_type)
        if "CONTROLLER" in ctype or "CONSUMER" in ctype or "CLI" in ctype:
            return DirectionEnum.DRIVING
        if "REPOSITORY" in ctype or "GATEWAY" in ctype or "PUBLISHER" in ctype or "ACL" in ctype:
            return DirectionEnum.DRIVEN
            
        return DirectionEnum.ANY