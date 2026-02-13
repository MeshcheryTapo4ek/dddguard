from dataclasses import dataclass, field
from pathlib import Path

import pytest

from dddguard.scanner.domain.graph_filtering_service import GraphFilteringService
from dddguard.shared.domain import (
    ArchetypeType,
    ComponentPassport,
    LayerEnum,
    ScopeEnum,
)

# --- MOCKS ---


@dataclass
class MockNode:
    file_path: Path
    passport: ComponentPassport

    # Minimal mock for finalize
    def finalize(self):
        pass


@dataclass
class MockGraph:
    nodes: dict = field(default_factory=dict)


class TestGraphFilteringService:
    @pytest.fixture
    def service(self):
        return GraphFilteringService

    @pytest.fixture
    def root_path(self, tmp_path):
        return tmp_path

    @pytest.fixture
    def sample_graph(self, root_path) -> MockGraph:
        """
        Creates a graph with various components.
        """

        def make_node(rel_path, scope, layer, ctx=None, ctype=ArchetypeType.UNKNOWN):
            return MockNode(
                file_path=root_path / rel_path,
                passport=ComponentPassport(
                    scope=scope,
                    layer=layer,
                    context_name=ctx,
                    component_type=ctype,
                    match_method="TEST",
                    direction="TEST",
                    macro_zone=None,
                ),
            )

        return MockGraph(
            nodes={
                # Code Nodes
                "billing.domain": make_node(
                    "src/billing/domain/model.py",
                    ScopeEnum.CONTEXT,
                    LayerEnum.DOMAIN,
                    "billing",
                ),
                "billing.app": make_node(
                    "src/billing/app/service.py",
                    ScopeEnum.CONTEXT,
                    LayerEnum.APP,
                    "billing",
                ),
                "ordering.domain": make_node(
                    "src/ordering/domain/model.py",
                    ScopeEnum.CONTEXT,
                    LayerEnum.DOMAIN,
                    "ordering",
                ),
                "shared.kernel": make_node(
                    "src/shared/kernel.py", ScopeEnum.SHARED, LayerEnum.DOMAIN, "shared"
                ),
                # Asset Node (Explicitly ASSET)
                "assets.data": make_node(
                    "src/assets/data.json",
                    ScopeEnum.CONTEXT,
                    LayerEnum.UNDEFINED,
                    "assets",
                    ctype=ArchetypeType.ASSET,
                ),
            }
        )

    def test_focus_path_filtering(self, service, sample_graph, root_path):
        """Scenario: User focuses on 'src/billing'. Only billing nodes should survive."""
        focus = root_path / "src/billing"

        result = service.determine_initial_focus(
            graph=sample_graph,
            focus_path=focus,
            whitelist_layers=None,
            whitelist_contexts=None,
            include_assets=True,
        )

        assert "billing.domain" in result
        assert "billing.app" in result
        assert "ordering.domain" not in result  # Outside folder
        assert "shared.kernel" not in result  # Outside folder & no context whitelist

    def test_shared_exception_inclusion(self, service, sample_graph, root_path):
        """
        Scenario: User wants to see 'Billing' AND 'Shared'.
        Previous logic used 'include_shared=True'.
        New logic requires explicit context whitelisting for both.
        """
        focus = root_path / "src/billing"

        result = service.determine_initial_focus(
            graph=sample_graph,
            focus_path=focus,
            whitelist_layers=None,
            # We must explicitly allow both to see both when filtering is active
            whitelist_contexts=["billing", "shared"],
            include_assets=True,
        )

        assert "billing.domain" in result
        assert "shared.kernel" in result
        assert "ordering.domain" not in result

    def test_context_whitelist(self, service, sample_graph, root_path):
        """Scenario: Focus on Root, but Whitelist context 'ordering'."""
        focus = root_path / "src"

        result = service.determine_initial_focus(
            graph=sample_graph,
            focus_path=focus,
            whitelist_layers=None,
            whitelist_contexts=["ordering"],
            include_assets=True,
        )

        assert "ordering.domain" in result
        assert "billing.domain" not in result
        assert "shared.kernel" not in result

    def test_layer_whitelist(self, service, sample_graph, root_path):
        """Scenario: Focus on Root, Whitelist layer 'APP'."""
        focus = root_path / "src"

        result = service.determine_initial_focus(
            graph=sample_graph,
            focus_path=focus,
            whitelist_layers=["APP"],
            whitelist_contexts=None,
            include_assets=True,
        )

        assert "billing.app" in result
        assert "billing.domain" not in result  # DOMAIN != APP
        assert "ordering.domain" not in result

    def test_asset_exclusion(self, service, sample_graph, root_path):
        """Scenario: include_assets=False."""
        focus = root_path / "src"

        result = service.determine_initial_focus(
            graph=sample_graph,
            focus_path=focus,
            whitelist_layers=None,
            whitelist_contexts=None,
            include_assets=False,  # <--- Exclude ASSETS
        )

        # "billing.domain" survives because its type is UNKNOWN (not ASSET)
        assert "billing.domain" in result

        # "assets.data" is hidden because its type is ASSET
        assert "assets.data" not in result
