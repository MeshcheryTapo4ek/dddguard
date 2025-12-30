from dataclasses import dataclass
from typing import List, ClassVar, Optional

from dddguard.shared import (
    LayerEnum,
    INTERNAL_ACCESS_MATRIX,
    PUBLIC_LAYERS,
    OUTBOUND_LAYERS,
    ScopeEnum,
)

# We now use LOCAL VOs
from ..value_objects import ViolationVo, ScannedNodeVo, ScannedImportVo


@dataclass(frozen=True, kw_only=True, slots=True)
class RuleEngineService:
    """
    Domain Service: Validates architectural dependency links.
    """

    _internal_matrix: ClassVar[dict] = INTERNAL_ACCESS_MATRIX
    _public_layers: ClassVar[set] = PUBLIC_LAYERS
    _outbound_layers: ClassVar[set] = OUTBOUND_LAYERS

    def check_dependency(
        self,
        source_node: ScannedNodeVo,
        link: ScannedImportVo,
    ) -> List[ViolationVo]:
        violations: List[ViolationVo] = []

        # 0. Preliminaries
        target_ctx = link.target_context
        if not target_ctx or not link.target_layer:
            return []

        # Map string layer to Enum for logic check
        try:
            source_layer_enum = LayerEnum(source_node.layer)
            target_layer_enum = LayerEnum(link.target_layer)
        except ValueError:
            # If layer is unknown/undefined, skip check or handle strictly
            return []

        # Skip technical layers
        if source_layer_enum in [LayerEnum.COMPOSITION, LayerEnum.GLOBAL]:
            return []

        # 1. Intra-Context Rules
        if source_node.context == target_ctx:
            violation = self._check_internal_access(
                source_node, source_layer_enum, target_layer_enum, link.target_module
            )
            if violation:
                violations.append(violation)

        # 2. Inter-Context Rules
        else:
            violations.extend(
                self._check_cross_context_access(
                    source_node,
                    source_layer_enum,
                    target_ctx,
                    target_layer_enum,
                    link.target_module,
                )
            )

        return violations

    def _check_internal_access(
        self,
        source: ScannedNodeVo,
        source_layer: LayerEnum,
        target_layer: LayerEnum,
        target_module: str,
    ) -> Optional[ViolationVo]:
        if source_layer not in self._internal_matrix:
            return None

        rule = self._internal_matrix[source_layer]

        if target_layer in rule.get("forbidden", set()):
            return ViolationVo(
                rule_id="R100",
                severity="error",
                message=f"Layer violation: '{source_layer}' cannot import '{target_layer}'",
                source_module=source.module_path,
                source_layer=str(source_layer),
                target_module=target_module,
                target_layer=str(target_layer),
                target_context=source.context,
            )
        return None

    def _check_cross_context_access(
        self,
        source: ScannedNodeVo,
        source_layer: LayerEnum,
        target_ctx: str,
        target_layer: LayerEnum,
        target_module: str,
    ) -> List[ViolationVo]:
        violations: List[ViolationVo] = []

        if target_ctx == "shared" or target_ctx == str(ScopeEnum.SHARED).lower():
            return []

        if source_layer not in self._outbound_layers:
            violations.append(
                ViolationVo(
                    rule_id="C201",
                    severity="error",
                    message=f"Context isolation: '{source_layer}' layer cannot initiate cross-context calls.",
                    source_module=source.module_path,
                    source_layer=str(source_layer),
                    target_module=target_module,
                    target_layer=str(target_layer),
                    target_context=target_ctx,
                )
            )

        if target_layer not in self._public_layers:
            violations.append(
                ViolationVo(
                    rule_id="C202",
                    severity="error",
                    message=f"Private access: Cannot import layer '{target_layer}' of context '{target_ctx}'.",
                    source_module=source.module_path,
                    source_layer=str(source_layer),
                    target_module=target_module,
                    target_layer=str(target_layer),
                    target_context=target_ctx,
                )
            )

        return violations
