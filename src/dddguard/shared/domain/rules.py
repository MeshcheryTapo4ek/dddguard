from dataclasses import dataclass
from typing import List, Optional
import re

from .enums import ProjectBoundedContextNames, ContextLayerEnum, AnyComponentType


@dataclass(frozen=True, slots=True)
class ClassificationRule:
    """
    Defines a rule to identify a specific architectural component
    based on file paths and naming conventions.
    """
    scope: ProjectBoundedContextNames
    layer: ContextLayerEnum
    component_type: AnyComponentType
    naming_protocols: List[str]
    path_pattern: Optional[str] = None

    def matches(
        self,
        relative_path_parts: tuple,
        filename_stem: str,
        layer_hint: Optional[ContextLayerEnum] = None,
    ) -> bool:
        """
        Determines if the provided file metadata matches this rule.
        """
        filename_str = filename_stem.lower()
        path_str = "/".join(relative_path_parts).lower()

        # 1. Enforce Layer Hint (if provided)
        if layer_hint and layer_hint != ContextLayerEnum.OTHER:
            if self.layer != layer_hint:
                return False
        
        # 2. Heuristic Safeguard:
        # Prevent Domain/App rules from triggering inside explicit 'adapters' directories.
        elif self._is_misplaced_core_component(path_str):
            return False

        # 3. Path Pattern Check
        if self.path_pattern:
            if not re.search(self.path_pattern, path_str, re.IGNORECASE):
                return False

        # 4. Naming Protocol Check
        for pattern in self.naming_protocols:
            if re.search(pattern, filename_str, re.IGNORECASE):
                return True

        return False

    def _is_misplaced_core_component(self, path_str: str) -> bool:
        """
        Checks if a Core rule (Domain/App) is being applied to an Infrastructure path.
        """
        if self.layer in [ContextLayerEnum.COMPOSITION, ContextLayerEnum.OTHER]:
            return False
            
        if "shared" in path_str:
            return False
            
        is_core_rule = self.layer in [ContextLayerEnum.DOMAIN, ContextLayerEnum.APP]
        is_adapter_path = "adapters" in path_str
        
        return is_core_rule and is_adapter_path