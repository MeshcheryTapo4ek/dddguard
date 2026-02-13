"""
Unit tests for GraphFilteringService.prune_graph().

prune_graph is a static method that mutates node statuses:
- Nodes in the visible set -> FINALIZED
- Nodes outside the visible set -> remain CLASSIFIED
"""

from dddguard.scanner.domain import GraphFilteringService
from dddguard.shared.domain import NodeStatus
from tests.scanner.conftest import make_classified_graph


class TestPruneGraph:
    """All branches of ``GraphFilteringService.prune_graph``."""

    def test_visible_nodes_become_finalized(self):
        graph = make_classified_graph(
            [
                {"path": "billing.domain.order"},
                {"path": "billing.domain.item"},
                {"path": "billing.app.create_order"},
            ]
        )

        visible = {"billing.domain.order", "billing.app.create_order"}
        result = GraphFilteringService.prune_graph(graph=graph, visible_modules=visible)

        assert result == visible
        assert graph.nodes["billing.domain.order"].status == NodeStatus.FINALIZED
        assert graph.nodes["billing.app.create_order"].status == NodeStatus.FINALIZED

    def test_non_visible_nodes_stay_classified(self):
        graph = make_classified_graph(
            [
                {"path": "billing.domain.order"},
                {"path": "billing.domain.item"},
            ]
        )

        visible = {"billing.domain.order"}
        GraphFilteringService.prune_graph(graph=graph, visible_modules=visible)

        assert graph.nodes["billing.domain.item"].status == NodeStatus.CLASSIFIED

    def test_empty_visible_set_leaves_all_classified(self):
        graph = make_classified_graph(
            [
                {"path": "a.b.c"},
                {"path": "x.y.z"},
            ]
        )

        result = GraphFilteringService.prune_graph(graph=graph, visible_modules=set())

        assert result == set()
        for node in graph.nodes.values():
            assert node.status == NodeStatus.CLASSIFIED

    def test_non_existent_node_ids_are_ignored(self):
        """IDs that don't exist in the graph should not cause errors."""
        graph = make_classified_graph(
            [
                {"path": "billing.domain.order"},
            ]
        )

        visible = {"billing.domain.order", "no.such.node", "another.fake"}
        result = GraphFilteringService.prune_graph(graph=graph, visible_modules=visible)

        # Only the real node gets finalized
        assert "billing.domain.order" in result
        assert graph.nodes["billing.domain.order"].status == NodeStatus.FINALIZED

    def test_all_nodes_visible(self):
        """When every node is visible, every node should be FINALIZED."""
        graph = make_classified_graph(
            [
                {"path": "a"},
                {"path": "b"},
                {"path": "c"},
            ]
        )

        all_paths = set(graph.nodes.keys())
        result = GraphFilteringService.prune_graph(graph=graph, visible_modules=all_paths)

        assert result == all_paths
        for node in graph.nodes.values():
            assert node.status == NodeStatus.FINALIZED
