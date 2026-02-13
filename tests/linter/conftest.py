"""
Shared fixtures and factories for Linter context tests.
"""

from pathlib import Path

import pytest

from dddguard.shared.domain import (
    CodeGraph,
    CodeNode,
    ComponentPassport,
    ComponentType,
    DirectionEnum,
    LayerEnum,
    MatchMethod,
    ScopeEnum,
)

# ==============================================================================
# FACTORIES
# ==============================================================================


def make_passport(
    scope: ScopeEnum = ScopeEnum.CONTEXT,
    context_name: str = "test_ctx",
    macro_zone: str | None = None,
    layer: LayerEnum = LayerEnum.DOMAIN,
    direction: DirectionEnum = DirectionEnum.NONE,
    component_type: ComponentType = "ENTITY",
    match_method: MatchMethod = MatchMethod.STRUCTURAL,
) -> ComponentPassport:
    """Factory for creating ComponentPassport instances."""
    return ComponentPassport(
        scope=scope,
        context_name=context_name,
        macro_zone=macro_zone,
        layer=layer,
        direction=direction,
        component_type=component_type,
        match_method=match_method,
    )


def make_node(
    path: str,
    *,
    passport: ComponentPassport | None = None,
    imports: frozenset[str] | None = None,
) -> CodeNode:
    """Factory for creating CodeNode instances."""
    node = CodeNode(
        path=path,
        file_path=Path(path) if path else None,
        content="",
    )
    node.passport = passport or make_passport()
    # Convert FrozenSet to Set (CodeNode.imports is mutable)
    if imports:
        node.imports = set(imports)
    return node


def make_graph(*nodes: CodeNode) -> CodeGraph:
    """Factory for creating CodeGraph from nodes."""
    graph = CodeGraph()
    for node in nodes:
        # Directly insert into graph (bypass add_node factory method)
        graph.nodes[node.path] = node
    return graph


# ==============================================================================
# FIXTURES
# ==============================================================================


@pytest.fixture
def rule_engine():
    """Provides a RuleEngineService instance for tests."""
    from dddguard.linter.domain import RuleEngineService

    return RuleEngineService()
