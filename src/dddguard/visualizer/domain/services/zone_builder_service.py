from dataclasses import dataclass, field
from typing import Dict, List, Any, Tuple

from dddguard.shared import (
    ContextLayerEnum, 
    AppTypeEnum, 
    DomainTypeEnum,
    DrivingAdapterEnum,
    DrivenAdapterEnum
)

from dddguard.scanner.domain import DependencyNode
from .styling.style_service import StyleService


@dataclass(frozen=True, kw_only=True, slots=True)
class ZoneBuilderService:
    """
    Domain Service: maps logical DDD nodes to visual zones and rows.
    """
    style: StyleService = field(default_factory=StyleService)

    def build_context_structure(self, nodes: List[DependencyNode]) -> Dict[str, Any]:
        """
        Builds a hierarchical structure: zone -> row -> side -> [node_data].
        FILTERS OUT ERROR OBJECTS to reduce visual noise.
        """
        structure: Dict[str, Dict[int, Dict[str, List[Dict[str, Any]]]]] = {
            "PORTS": {},
            "ADAPTERS": {},
            "APP": {},
            "DOMAIN": {},
            "COMPOSITION": {},
            "OTHER": {},
        }

        for node in nodes:
            # --- FILTER: Skip Errors globally ---
            if self._is_error_node(node):
                continue

            zone, row, side = self._get_placement(node.layer, node.component_type)

            if zone not in structure:
                structure[zone] = {}

            if row not in structure[zone]:
                structure[zone][row] = {"left": [], "right": [], "center": []}

            node_data = self._create_box_data(node)
            structure[zone][row][side].append(node_data)

        return structure

    def _is_error_node(self, node: DependencyNode) -> bool:
        """
        Checks if the node represents an Exception or Error component.
        """
        # Check explicit Enum types
        if node.component_type in (
            DomainTypeEnum.DOMAIN_ERROR,
            AppTypeEnum.APP_ERROR,
            DrivenAdapterEnum.ADAPTER_ERROR,
            DrivingAdapterEnum.ADAPTER_ERROR,
        ):
            return True
            
        # Check string representation (fallback)
        type_str = str(node.component_type)
        if "Error" in type_str or "Exception" in type_str:
            return True
            
        return False

    def _get_placement(
        self,
        layer: ContextLayerEnum,
        type_val: Any,
    ) -> Tuple[str, int, str]:
        """
        Returns tuple of (zone_name, row_index, side_alignment).
        """

        # --- 1. PORTS ---
        if layer == ContextLayerEnum.DRIVING_PORTS:
            return "PORTS", 0, "left"
        if layer == ContextLayerEnum.DRIVEN_PORTS:
            return "PORTS", 0, "right"

        # --- 2. ADAPTERS ---
        is_driving_adapter = layer == ContextLayerEnum.DRIVING_ADAPTERS
        is_driven_adapter = layer == ContextLayerEnum.DRIVEN_ADAPTERS
        is_dto = layer in (ContextLayerEnum.DRIVING_DTO, ContextLayerEnum.DRIVEN_DTO)
        
        # (Error handling logic removed here as we filter them upfront)

        if is_dto:
            side = "left" if (layer == ContextLayerEnum.DRIVING_DTO) else "right"
            return "ADAPTERS", 0, side

        if is_driving_adapter:
            return "ADAPTERS", 1, "left"
        
        if is_driven_adapter:
            return "ADAPTERS", 1, "right"

        # --- 3. APP LAYER ---
        if layer == ContextLayerEnum.APP:
            # (Error handling removed)

            # Row 0: Entry Points
            if type_val == AppTypeEnum.INTERFACE or str(type_val) == "Interface":
                return "APP", 0, "right" 
            if type_val == AppTypeEnum.HANDLER:
                return "APP", 0, "left"

            # Row 1: Orchestration
            if type_val == AppTypeEnum.WORKFLOW:
                return "APP", 1, "center"

            # Row 2: Main Logic
            if type_val == AppTypeEnum.QUERY:
                return "APP", 2, "right"
            
            return "APP", 2, "left"

        # --- 4. DOMAIN LAYER ---
        if layer == ContextLayerEnum.DOMAIN:
            # (Error handling removed)

            # Row 0: Pure Services
            if type_val == DomainTypeEnum.DOMAIN_SERVICE:
                return "DOMAIN", 0, "center"
            
            # Row 1: Main Aggregates/Entities
            if type_val in (DomainTypeEnum.AGGREGATE_ROOT, DomainTypeEnum.ENTITY, DomainTypeEnum.FACTORY):
                return "DOMAIN", 1, "center"

            # Row 2: Values (VOs, Events)
            return "DOMAIN", 2, "center"

        # --- 5. COMPOSITION ---
        if layer == ContextLayerEnum.COMPOSITION:
            return "COMPOSITION", 0, "center"

        # --- 6. Fallback ---
        return "OTHER", 0, "center"

    def _create_box_data(self, node: DependencyNode) -> Dict[str, Any]:
        type_str = node.component_type.value if hasattr(node.component_type, "value") else str(node.component_type)
        label = self.style.format_label(node.module_path, type_str)
        imports = [{"module": link.target_module} for link in node.imports]

        return {
            "label": label,
            "width": self.style.calculate_node_width(label),
            "height": self.style.NODE_HEIGHT,
            "color": self.style.get_node_color(node.layer),
            "raw_type": type_str,
            "id": node.module_path,
            "layer": node.layer,
            "context": node.context,
            "imports": imports,
        }

    def sum_width(self, items: List[Dict[str, Any]]) -> float:
        if not items:
            return 0.0
        return sum(n["width"] for n in items) + (len(items) - 1) * self.style.NODE_GAP_X