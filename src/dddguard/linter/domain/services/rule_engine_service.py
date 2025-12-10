from dataclasses import dataclass
from typing import List, ClassVar

from dddguard.shared import ContextLayerEnum
from dddguard.shared.assets import (
    INTERNAL_ACCESS_MATRIX,
    PUBLIC_LAYERS,
    OUTBOUND_LAYERS,
)
from dddguard.scanner.domain import DependencyNode, DependencyLink
from ..value_objects import ViolationVo


@dataclass(frozen=True, kw_only=True, slots=True)
class RuleEngineService:
    """
    Domain Service: Validates dependencies against architectural rules.
    """
    
    _internal_matrix: ClassVar[dict] = INTERNAL_ACCESS_MATRIX
    _public_layers: ClassVar[set] = PUBLIC_LAYERS
    _outbound_layers: ClassVar[set] = OUTBOUND_LAYERS

    def check_dependency(
        self,
        source_node: DependencyNode,
        link: DependencyLink,
    ) -> List[ViolationVo]:
        """
        Validates a single dependency link from source node.
        """
        violations = []

        # 0. Preliminaries
        target_ctx = link.target_context
        if not target_ctx or link.target_type is None:
            return []

        # Ignore Composition layer checks
        if source_node.layer in [ContextLayerEnum.COMPOSITION, ContextLayerEnum.OTHER]:
            return []
        
        try:
            target_layer = ContextLayerEnum(link.target_layer)
        except ValueError:
            return [] 

        # 1. Intra-Context Rules (Same Context)
        if source_node.context == target_ctx:
            violation = self._check_internal_access(source_node, target_layer, link.target_module)
            if violation:
                violations.append(violation)

        # 2. Inter-Context Rules (Cross Context)
        else:
            violations.extend(
                self._check_cross_context_access(source_node, target_ctx, target_layer, link.target_module)
            )

        return violations

    def _check_internal_access(
        self, 
        source: DependencyNode, 
        target_layer: ContextLayerEnum, 
        target_module: str
    ) -> ViolationVo | None:
        """R1xx: Layer Isolation Rules (Intra-Context)."""
        
        if source.layer not in self._internal_matrix:
            return None

        rule = self._internal_matrix[source.layer]
        
        if target_layer in rule.get("forbidden", set()):
            return ViolationVo(
                rule_id="R100",
                severity="error",
                message=f"Layer violation: '{source.layer.value}' cannot import '{target_layer.value}'",
                source_module=source.module_path,
                source_layer=source.layer.value,
                target_module=target_module,
                target_layer=target_layer.value,
                target_context=source.context,
            )
        return None

    def _check_cross_context_access(
        self,
        source: DependencyNode,
        target_ctx: str,
        target_layer: ContextLayerEnum,
        target_module: str
    ) -> List[ViolationVo]:
        """C2xx: Cross-Context Rules (Inter-Context)."""
        violations = []

        # Shared Kernel is always allowed unless specific restrictions apply
        if target_ctx == "shared":
            return []

        # Rule C201: Who can initiate?
        if source.layer not in self._outbound_layers:
            violations.append(
                ViolationVo(
                    rule_id="C201",
                    severity="error",
                    message=f"Context isolation: '{source.layer.value}' layer cannot initiate cross-context calls. Use an Adapter/ACL.",
                    source_module=source.module_path,
                    source_layer=source.layer.value,
                    target_module=target_module,
                    target_layer=target_layer.value,
                    target_context=target_ctx,
                )
            )

        # Rule C202: What can be accessed?
        if target_layer not in self._public_layers:
            violations.append(
                ViolationVo(
                    rule_id="C202",
                    severity="error",
                    message=f"Private access: Cannot import private layer '{target_layer.value}' of context '{target_ctx}'. Use DTOs or Public API.",
                    source_module=source.module_path,
                    source_layer=source.layer.value,
                    target_module=target_module,
                    target_layer=target_layer.value,
                    target_context=target_ctx,
                )
            )
        
        return violations