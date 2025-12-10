from dataclasses import dataclass
from typing import Tuple, Optional

from dddguard.shared import (
    ClassificationRule,
    ProjectBoundedContextNames,
    ContextLayerEnum,
)
from dddguard.shared.assets import RULES_REGISTRY

@dataclass(frozen=True, kw_only=True, slots=True)
class RegexMatcherService:
    """
    Domain Service: Level 3 - Protocol-based classification.
    Matches files based on strict Naming Protocols defined in the registry.
    """

    def match(
        self,
        scope: ProjectBoundedContextNames,
        path_parts: Tuple[str, ...],
        filename: str,
        layer_hint: Optional[ContextLayerEnum] = None,
    ) -> Optional[ClassificationRule]:
        """
        Finds a rule where the filename adheres to a naming protocol.
        """
        # Filter rules by scope first to reduce iterations
        candidates = [r for r in RULES_REGISTRY if r.scope == scope]

        # Prioritize checking protocols for the hinted layer
        if layer_hint and layer_hint != ContextLayerEnum.OTHER:
            candidates.sort(key=lambda r: r.layer != layer_hint)

        for rule in candidates:
            if rule.matches(path_parts, filename, layer_hint):
                return rule

        return None