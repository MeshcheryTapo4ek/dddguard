from dataclasses import dataclass
from typing import ClassVar

from dddguard.shared.domain import (
    COMPOSITION_LAYERS,
    CROSS_CONTEXT_INBOUND_ALLOWED,
    CROSS_CONTEXT_OUTBOUND_ALLOWED,
    FRACTAL_DOWNSTREAM_ALLOWED,
    FRACTAL_UPSTREAM_FORBIDDEN,
    INTERNAL_ACCESS_MATRIX,
    CodeGraph,
    CodeNode,
    InternalAccessMatrix,
    LayerDirectionKey,
    ScopeEnum,
)

from .events import ViolationEvent


@dataclass(frozen=True, kw_only=True, slots=True)
class RuleEngineService:
    """
    Domain Service: Validates architectural dependency links.
    Implements 13 rules across 4 groups (Internal, Fractal, Cross-Context, Scope).
    """

    _internal_matrix: ClassVar[InternalAccessMatrix] = INTERNAL_ACCESS_MATRIX

    def check_node(
        self,
        source_node: CodeNode,
        graph: CodeGraph,
    ) -> list[ViolationEvent]:
        """
        Validates all imports of a source node against architectural rules.
        Returns a list of violations (empty if all imports are valid).
        """
        violations: list[ViolationEvent] = []

        if not source_node.passport:
            return []

        for target_path in source_node.imports:
            target_node = graph.get_node(target_path)
            if not target_node or not target_node.passport:
                continue

            violation = self._validate_link(source_node, target_node, target_path)
            if violation:
                violations.append(violation)

        return violations

    def _validate_link(
        self,
        source: CodeNode,
        target: CodeNode,
        target_path_str: str,
    ) -> ViolationEvent | None:
        """
        Validates a single import link. Returns a ViolationEvent if invalid, None otherwise.

        Rule application order:
        1. Bypass conditions
        2. Scope isolation (Shared, Root)
        3. Same context (internal rules)
        4. Fractal kinship (parent-child)
        5. Alien contexts (cross-context)
        """
        src_pass = source.passport
        tgt_pass = target.passport

        if not src_pass or not tgt_pass:
            return None

        # --- STEP 1: BYPASS CONDITIONS ---
        if self._check_bypass(src_pass.scope, src_pass.layer, tgt_pass.scope):
            return None

        # --- STEP 2: SCOPE ISOLATION RULES (Group 4) ---
        scope_violation = self._check_scope_isolation(
            source.path, src_pass.scope, tgt_pass.scope, target_path_str
        )
        if scope_violation:
            return scope_violation

        # --- STEP 3: DETERMINE RELATIONSHIP ---
        src_ctx = src_pass.context_name or "unknown"
        tgt_ctx = tgt_pass.context_name or "unknown"

        # Same context?
        if src_pass.scope == ScopeEnum.CONTEXT and tgt_pass.scope == ScopeEnum.CONTEXT:
            if src_ctx == tgt_ctx:
                return self._check_internal_access(
                    source.path,
                    src_pass.layer,
                    src_pass.direction,
                    tgt_pass.layer,
                    tgt_pass.direction,
                    target_path_str,
                    src_ctx,
                )

        # Fractal kinship?
        # Upstream: Child -> Parent (source.macro_zone == target.context_name)
        if src_pass.macro_zone == tgt_ctx:
            return self._check_fractal_upstream(
                source.path,
                src_ctx,
                tgt_pass.layer,
                tgt_pass.direction,
                tgt_ctx,
                target_path_str,
            )

        # Downstream: Parent -> Child (target.macro_zone == source.context_name)
        if tgt_pass.macro_zone == src_ctx:
            return self._check_fractal_downstream(
                source.path,
                src_ctx,
                tgt_pass.layer,
                tgt_pass.direction,
                tgt_ctx,
                target_path_str,
            )

        # --- STEP 4: ALIEN CONTEXTS (Group 3: Cross-Context Rules) ---
        return self._check_cross_context(
            source.path,
            src_pass.layer,
            src_pass.direction,
            tgt_pass.layer,
            tgt_pass.direction,
            tgt_ctx,
            target_path_str,
        )

    # ==========================================================================
    # BYPASS CONDITIONS
    # ==========================================================================

    def _check_bypass(self, src_scope: ScopeEnum, src_layer, tgt_scope: ScopeEnum) -> bool:
        """
        Returns True if the import should skip all rule checks.

        Bypass conditions:
        - Target is SHARED -> always allowed (global shared kernel)
        - Source is COMPOSITION or GLOBAL -> can import anything within context
        """
        # Target is global shared kernel -> always allowed
        if tgt_scope == ScopeEnum.SHARED:
            return True

        # Source is composition/wiring layer -> can import anything within context
        return src_layer in COMPOSITION_LAYERS

    # ==========================================================================
    # GROUP 4: SCOPE ISOLATION RULES
    # ==========================================================================

    def _check_scope_isolation(
        self,
        src_path: str,
        src_scope: ScopeEnum,
        tgt_scope: ScopeEnum,
        tgt_path: str,
    ) -> ViolationEvent | None:
        """
        Rules 12-13: Shared Independence, Root Isolation
        """
        # Rule 12: Shared Independence
        # Shared cannot import from CONTEXT or ROOT
        if src_scope == ScopeEnum.SHARED:
            if tgt_scope in (ScopeEnum.CONTEXT, ScopeEnum.ROOT):
                return ViolationEvent(
                    rule_name="Shared Independence",
                    severity="error",
                    message="Shared kernel cannot depend on bounded contexts or root. "
                    "Shared is the base of the pyramid.",
                    source_module=src_path,
                    source_layer="shared",
                    target_module=tgt_path,
                    target_layer=tgt_scope.value.lower(),
                    target_context="N/A",
                )

        # Rule 13: Root Isolation
        # Root can only import providers and shared
        # This is enforced at file level: root should only touch <context>/provider.py
        # For now, we skip this check in the linter (it's a structural convention)
        # but we could add a stricter check if needed

        return None

    # ==========================================================================
    # GROUP 1: INTERNAL RULES (Same Context)
    # ==========================================================================

    def _check_internal_access(
        self,
        src_path: str,
        src_layer,
        src_direction,
        tgt_layer,
        tgt_direction,
        tgt_path: str,
        ctx: str,
    ) -> ViolationEvent | None:
        """
        Rules 1-7: Domain Purity, App Isolation, Driving Port Boundary,
        Driven Port Boundary, Driving Adapter Boundary, Driven Adapter Boundary, Composition
        """
        src_key: LayerDirectionKey = (src_layer, src_direction)
        tgt_key: LayerDirectionKey = (tgt_layer, tgt_direction)

        if src_key not in self._internal_matrix:
            # Unknown source layer/direction combo -> skip
            return None

        rule = self._internal_matrix[src_key]

        # Check if target is in the forbidden set
        if tgt_key in rule["forbidden"]:
            # Determine rule name based on source
            from typing import cast

            from dddguard.shared.domain import RuleName

            rule_name_map: dict[tuple[str, str], RuleName] = {
                ("DOMAIN", "NONE"): "Domain Purity",
                ("APP", "NONE"): "App Isolation",
                ("PORTS", "DRIVING"): "Driving Port Boundary",
                ("PORTS", "DRIVEN"): "Driven Port Boundary",
                ("ADAPTERS", "DRIVING"): "Driving Adapter Boundary",
                ("ADAPTERS", "DRIVEN"): "Driven Adapter Boundary",
            }
            rule_name = rule_name_map.get(
                (src_layer.value, src_direction.value),
                cast(RuleName, "Domain Purity"),  # Fallback (shouldn't happen)
            )

            return ViolationEvent(
                rule_name=rule_name,
                severity="error",
                message=f"Layer '{src_layer.value}/{src_direction.value}' cannot import "
                f"'{tgt_layer.value}/{tgt_direction.value}' within the same context.",
                source_module=src_path,
                source_layer=f"{src_layer.value}/{src_direction.value}",
                target_module=tgt_path,
                target_layer=f"{tgt_layer.value}/{tgt_direction.value}",
                target_context=ctx,
            )

        return None

    # ==========================================================================
    # GROUP 2: FRACTAL RULES (Parent ↔ Child)
    # ==========================================================================

    def _check_fractal_upstream(
        self,
        src_path: str,
        src_ctx: str,
        tgt_layer,
        tgt_direction,
        tgt_ctx: str,
        tgt_path: str,
    ) -> ViolationEvent | None:
        """
        Rule 8: Fractal Upstream Access
        Child -> Parent: can import Domain, App, Ports/Driven
        """
        tgt_key: LayerDirectionKey = (tgt_layer, tgt_direction)

        if tgt_key in FRACTAL_UPSTREAM_FORBIDDEN:
            return ViolationEvent(
                rule_name="Fractal Upstream Access",
                severity="error",
                message=f"Child context '{src_ctx}' can only access parent '{tgt_ctx}' "
                f"Domain, App, and Driven Ports (local shared kernel). "
                f"Cannot access '{tgt_layer.value}/{tgt_direction.value}'.",
                source_module=src_path,
                source_layer="child",
                target_module=tgt_path,
                target_layer=f"{tgt_layer.value}/{tgt_direction.value}",
                target_context=tgt_ctx,
            )

        return None

    def _check_fractal_downstream(
        self,
        src_path: str,
        src_ctx: str,
        tgt_layer,
        tgt_direction,
        tgt_ctx: str,
        tgt_path: str,
    ) -> ViolationEvent | None:
        """
        Rule 9: Fractal Downstream Access
        Parent -> Child: can only import Ports/Driving (facades)
        """
        tgt_key: LayerDirectionKey = (tgt_layer, tgt_direction)

        if tgt_key not in FRACTAL_DOWNSTREAM_ALLOWED:
            return ViolationEvent(
                rule_name="Fractal Downstream Access",
                severity="error",
                message=f"Parent context '{src_ctx}' can only access child '{tgt_ctx}' "
                f"via Public Driving Ports (facades). "
                f"Cannot access '{tgt_layer.value}/{tgt_direction.value}'.",
                source_module=src_path,
                source_layer="parent",
                target_module=tgt_path,
                target_layer=f"{tgt_layer.value}/{tgt_direction.value}",
                target_context=tgt_ctx,
            )

        return None

    # ==========================================================================
    # GROUP 3: CROSS-CONTEXT RULES (Alien Contexts)
    # ==========================================================================

    def _check_cross_context(
        self,
        src_path: str,
        src_layer,
        src_direction,
        tgt_layer,
        tgt_direction,
        tgt_ctx: str,
        tgt_path: str,
    ) -> ViolationEvent | None:
        """
        Rules 10-11: Cross-Context Outbound, Cross-Context Inbound
        """
        src_key: LayerDirectionKey = (src_layer, src_direction)
        tgt_key: LayerDirectionKey = (tgt_layer, tgt_direction)

        # Rule 10: Cross-Context Outbound
        # Only Ports/Driven (ACL) can initiate calls to other contexts
        if src_key not in CROSS_CONTEXT_OUTBOUND_ALLOWED:
            return ViolationEvent(
                rule_name="Cross-Context Outbound",
                severity="error",
                message=f"Layer '{src_layer.value}/{src_direction.value}' cannot initiate "
                f"cross-context calls. Only Driven Ports (ACL) may access other contexts.",
                source_module=src_path,
                source_layer=f"{src_layer.value}/{src_direction.value}",
                target_module=tgt_path,
                target_layer=f"{tgt_layer.value}/{tgt_direction.value}",
                target_context=tgt_ctx,
            )

        # Rule 11: Cross-Context Inbound
        # Can only call Ports/Driving of other contexts
        if tgt_key not in CROSS_CONTEXT_INBOUND_ALLOWED:
            return ViolationEvent(
                rule_name="Cross-Context Inbound",
                severity="error",
                message=f"Cannot import internal layer '{tgt_layer.value}/{tgt_direction.value}' "
                f"of context '{tgt_ctx}'. Only Driving Ports (public API) are accessible.",
                source_module=src_path,
                source_layer=f"{src_layer.value}/{src_direction.value}",
                target_module=tgt_path,
                target_layer=f"{tgt_layer.value}/{tgt_direction.value}",
                target_context=tgt_ctx,
            )

        return None
