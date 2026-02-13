"""
Shared fixtures for the Scanner context test suite.

Provides factory helpers for domain objects used across unit, flow,
integration and E2E tests.
"""

from pathlib import Path

import pytest

from dddguard.shared.domain import (
    ArchetypeType,
    CodeGraph,
    CodeNode,
    ComponentPassport,
    DirectionEnum,
    LayerEnum,
    MatchMethod,
    ScannerConfig,
    ScopeEnum,
)

# ---------------------------------------------------------------------------
# Factory Helpers (not fixtures — used imperatively in tests)
# ---------------------------------------------------------------------------


def make_passport(**overrides) -> ComponentPassport:
    """
    Creates a ComponentPassport with sensible defaults.
    Any field can be overridden via kwargs.
    """
    defaults = dict(
        scope=ScopeEnum.CONTEXT,
        context_name="billing",
        macro_zone=None,
        layer=LayerEnum.DOMAIN,
        direction=DirectionEnum.NONE,
        component_type=ArchetypeType.UNKNOWN,
        match_method=MatchMethod.STRUCTURAL,
    )
    defaults.update(overrides)
    return ComponentPassport(**defaults)


def make_node(
    path: str,
    *,
    file_path: Path | None = None,
    status: str = "classified",
    passport: ComponentPassport | None = None,
    imports: set | None = None,
) -> CodeNode:
    """
    Creates a CodeNode at a given lifecycle stage.

    ``status`` can be: "detected", "linked", "classified", "finalized".
    If ``status`` >= "classified" a passport is auto-created unless one is provided.
    """
    node = CodeNode(path=path, file_path=file_path)

    if status in ("linked", "classified", "finalized"):
        node.link_imports(list(imports or []))

    if status in ("classified", "finalized"):
        pp = passport or make_passport(context_name=path.split(".")[0])
        node.classify(pp)

    if status == "finalized":
        node.finalize()

    return node


def make_classified_graph(node_specs: list[dict]) -> CodeGraph:
    """
    Builds a CodeGraph where every node is CLASSIFIED.

    ``node_specs`` is a list of dicts, each with at minimum a ``path`` key.
    Optional keys: ``file_path``, ``passport``, ``imports``.

    Example::

        graph = make_classified_graph([
            {"path": "billing.domain.order", "imports": {"billing.domain.item"}},
            {"path": "billing.domain.item"},
        ])
    """
    graph = CodeGraph()
    for spec in node_specs:
        path = spec["path"]
        fp = spec.get("file_path")
        imports = spec.get("imports", set())
        passport = spec.get("passport", make_passport(context_name=path.split(".")[0]))

        node = graph.add_node(path=path, file_path=fp)
        node.link_imports(list(imports))
        node.classify(passport)

    return graph


# ---------------------------------------------------------------------------
# Pytest Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def default_scanner_config() -> ScannerConfig:
    """Returns a ScannerConfig with default test values."""
    return ScannerConfig()
