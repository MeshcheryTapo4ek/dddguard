"""
Flow tests for ClassificationFacade.

The facade is a thin pass-through to ClassifyGraphWorkflow.
"""

from unittest.mock import MagicMock

import pytest

from dddguard.scanner.classification.ports.driving.facade import ClassificationFacade
from dddguard.shared.domain import CodeGraph
from tests.scanner.conftest import make_classified_graph

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_workflow():
    return MagicMock()


@pytest.fixture
def facade(mock_workflow) -> ClassificationFacade:
    return ClassificationFacade(graph_workflow=mock_workflow)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestClassificationFacadeHappyPath:
    def test_delegates_to_workflow(self, facade, mock_workflow, tmp_path):
        graph = CodeGraph()
        source_dir = tmp_path / "src"

        expected = make_classified_graph([{"path": "a.b"}])
        mock_workflow.return_value = expected

        result = facade.classify_graph(graph=graph, source_dir=source_dir)

        assert result is expected
        mock_workflow.assert_called_once_with(graph=graph, source_dir=source_dir)


class TestClassificationFacadeNoneSourceDir:
    def test_source_dir_none_forwarded(self, facade, mock_workflow):
        """When source_dir=None, it should be forwarded as-is."""
        graph = CodeGraph()
        facade.classify_graph(graph=graph, source_dir=None)

        mock_workflow.assert_called_once_with(graph=graph, source_dir=None)
