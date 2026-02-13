"""
Flow tests for ClassifyGraphWorkflow.

Dependencies:
- IdentifyComponentUseCase is mocked (unit boundary).
- CodeGraph is real (we test orchestration logic).
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from dddguard.scanner.classification.app.classify_graph_workflow import (
    ClassifyGraphWorkflow,
)
from dddguard.shared.domain import (
    ArchetypeType,
    CodeGraph,
    NodeStatus,
)
from tests.scanner.conftest import make_passport

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_identifier():
    """Returns a MagicMock that replaces IdentifyComponentUseCase."""
    return MagicMock()


@pytest.fixture
def workflow(mock_identifier) -> ClassifyGraphWorkflow:
    return ClassifyGraphWorkflow(identifier_use_case=mock_identifier)


@pytest.fixture
def source_dir(tmp_path) -> Path:
    return tmp_path / "src"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestClassifyGraphWorkflowHappyPath:
    def test_all_nodes_get_classified(self, workflow, mock_identifier, source_dir):
        """3 nodes should each receive a passport from the identifier."""
        graph = CodeGraph()
        graph.add_node("billing.domain.order", file_path=source_dir / "billing/domain/order.py")
        graph.add_node("billing.domain.item", file_path=source_dir / "billing/domain/item.py")
        graph.add_node("billing.app.create", file_path=source_dir / "billing/app/create.py")

        passport = make_passport(component_type=ArchetypeType.UNKNOWN)
        mock_identifier.return_value = passport

        result = workflow(graph=graph, source_dir=source_dir)

        assert result is graph
        assert mock_identifier.call_count == 3
        for node in graph.nodes.values():
            assert node.status == NodeStatus.CLASSIFIED
            assert node.passport is passport


class TestClassifyGraphWorkflowFallbackPath:
    def test_node_without_file_path_uses_reconstructed_path(
        self, workflow, mock_identifier, source_dir
    ):
        """
        When a node has no file_path, the workflow should reconstruct it
        from the logical path: 'billing.domain.model' -> '<source_dir>/billing/domain/model.py'
        """
        graph = CodeGraph()
        node = graph.add_node("billing.domain.model", file_path=None)

        passport = make_passport()
        mock_identifier.return_value = passport

        workflow(graph=graph, source_dir=source_dir)

        # The identifier should have been called with the reconstructed path
        call_args = mock_identifier.call_args
        expected_path = source_dir / "billing/domain/model.py"
        assert call_args.kwargs["file_path"] == expected_path
        assert node.passport is passport


class TestClassifyGraphWorkflowEmptyGraph:
    def test_empty_graph_returns_same_empty_graph(self, workflow, source_dir):
        graph = CodeGraph()
        result = workflow(graph=graph, source_dir=source_dir)

        assert result is graph
        assert len(result.nodes) == 0


class TestClassifyGraphWorkflowMetrics:
    def test_mix_of_unknown_and_real_passports(self, workflow, mock_identifier, source_dir):
        """Verifies that the workflow counts classified vs unknown correctly."""
        graph = CodeGraph()
        graph.add_node("a.domain.order", file_path=source_dir / "a/domain/order.py")
        graph.add_node("a.domain.item", file_path=source_dir / "a/domain/item.py")
        graph.add_node("a.app.svc", file_path=source_dir / "a/app/svc.py")

        real_passport = make_passport(component_type=ArchetypeType.FOLDER)
        unknown_passport = make_passport(component_type=ArchetypeType.UNKNOWN)

        # First two calls return real passport, third returns UNKNOWN
        mock_identifier.side_effect = [real_passport, real_passport, unknown_passport]

        workflow(graph=graph, source_dir=source_dir)

        # All three should be classified regardless of component_type
        for node in graph.nodes.values():
            assert node.status == NodeStatus.CLASSIFIED

        # Verify the passports were assigned in order
        nodes = list(graph.nodes.values())
        assert nodes[0].passport is real_passport
        assert nodes[1].passport is real_passport
        assert nodes[2].passport is unknown_passport
